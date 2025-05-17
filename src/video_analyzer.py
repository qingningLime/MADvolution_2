import os
import json
import time
import subprocess
import threading
from datetime import timedelta
import argparse
from tqdm import tqdm
import ollama
from httpx import ConnectError
from PIL import Image
import re

def get_video_fps(video_path):
    """使用FFmpeg获取视频实际帧率"""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=r_frame_rate',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    num, denom = map(int, result.stdout.strip().split('/'))
    return num / denom

def process_subtitles(video_path):
    """处理字幕文件并生成文本记录(改进版)"""
    # 获取视频所在目录
    video_dir = os.path.dirname(video_path)
    # 查找目录下的第一个.ass文件
    ass_files = [f for f in os.listdir(video_dir) if f.endswith('.ass')]
    
    # 创建固定名称的输出文件夹
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_dir = os.path.join('output', video_name)
    os.makedirs(output_dir, exist_ok=True)
    txt_path = os.path.join(output_dir, f"{video_name}_subtitles.txt")

    if not ass_files:
        print(f"\n警告: 未在视频目录中找到字幕文件(.ass)")
        while True:
            external_sub = input("请输入外部字幕文件路径(.txt格式): ").strip()
            if not external_sub:
                print("未提供字幕文件路径，跳过字幕处理")
                return None
            
            # 处理路径中的引号和空格
            external_sub = external_sub.strip('"\'')
            
            # 检查路径是否存在
            if not os.path.exists(external_sub):
                # 尝试处理带盘符的Windows路径
                if ':' in external_sub and not external_sub.startswith(('http://', 'https://')):
                    if not os.path.exists(external_sub.replace('\\', '/')):
                        print("文件不存在，请重新输入")
                        continue
                else:
                    print("文件不存在，请重新输入")
                    continue
            
            # 检查文件扩展名
            if not external_sub.lower().endswith('.txt'):
                print("仅支持.txt格式字幕文件")
                continue
            import shutil
            shutil.copy2(external_sub, txt_path)
            print(f"已复制字幕文件到: {txt_path}")
            return txt_path
    
    ass_path = os.path.join(video_dir, ass_files[0])
    

    normal_lines = []
    special_lines = []
    last_entries = {}  # 存储最后出现的字幕条目
    in_songs = {}      # 存储插入曲 {曲名: [(start, end, text), ...]}
    current_song = None
    
    with open(ass_path, 'r', encoding='utf-8') as f:
        in_events = False
        for line in f:
            line = line.strip()
            if line.startswith('[Events]'):
                in_events = True
                continue
            if not in_events:
                continue
                
            if line.startswith('Comment:') and 'IN「' in line:
                # 处理插入曲标记
                song_name = line.split('IN「')[1].split('」')[0]
                current_song = song_name
                if song_name not in in_songs:
                    in_songs[song_name] = []
            
            if line.startswith('Dialogue:'):
                parts = line.split(',', 9)
                if len(parts) < 10:
                    continue
                    
                start = parts[1].strip()
                end = parts[2].strip()
                style = parts[3].strip()
                text = parts[9].strip()
                
                # 去除所有特效标签
                text = re.sub(r'\{.*?\}', '', text)
                
                # 处理插入曲
                if style.startswith('IN_'):
                    if current_song:
                        in_songs[current_song].append((start, end, text))
                    else:
                        in_songs.setdefault("未命名插入曲", []).append((start, end, text))
                # 对于特效字幕(OP/ED)，检查是否与前一条目文本相同
                elif style in ['OP_CH', 'ED_CH']:
                    if text in last_entries:
                        # 合并时间范围，更新结束时间
                        last_start, last_end, last_style = last_entries[text]
                        if style == last_style:
                            last_entries[text] = (last_start, end, style)
                            continue
                    
                    # 新条目或不同样式，保存当前条目
                    last_entries[text] = (start, end, style)
                else:
                    # 普通对话直接添加
                    if style in ['Dial_CH']:
                        normal_lines.append(f"{start} --> {end}：{text}")
                    elif style in ['Lyric_CH']:
                        special_lines.append(f"{start} --> {end} [歌词]：{text}")
                    elif style in ['Title', 'Staff']:
                        special_lines.append(f"{start} --> {end} [标题/制作]：{text}")
    
    # 添加合并后的特效字幕
    for text, (start, end, style) in last_entries.items():
        if style == 'OP_CH':
            special_lines.append(f"{start} --> {end} [OP]：{text}")
        elif style == 'ED_CH':
            special_lines.append(f"{start} --> {end} [ED]：{text}")
    
    # 添加插入曲内容
    if in_songs:
        special_lines.append("\n插入曲：")
        for song_name, lyrics in in_songs.items():
            special_lines.append(f"\n【{song_name}】")
            for start, end, text in lyrics:
                special_lines.append(f"{start} --> {end}：{text}")
    
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("普通对话：\n")
        f.write("\n".join(normal_lines))
        f.write("\n\n特殊字幕：\n")
        f.write("\n".join(special_lines))
    
    return txt_path

def monitor_frames(output_dir):
    """监控并单行实时显示最新帧文件"""
    last_frame = None
    while True:
        if os.path.exists(output_dir):
            frames = [f for f in os.listdir(output_dir) if f.startswith('frame_')]
            if frames:
                latest = sorted(frames)[-1]
                if latest != last_frame:
                    print(f"\r最新关键帧: {os.path.join(output_dir, latest)}", end="", flush=True)
                    last_frame = latest

def extract_keyframes(video_path, output_dir, interval=5):
    """提取视频关键帧(使用GPU加速)"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 先处理字幕并确保完成
    subtitle_file = process_subtitles(video_path)
    if subtitle_file:
        print(f"已生成字幕文件: {subtitle_file}")
        # 确保字幕文件已完全写入

    
    # 启动监控线程
    monitor_thread = threading.Thread(
        target=monitor_frames,
        args=(output_dir,),
        daemon=True
    )
    monitor_thread.start()
    
    cmd = [
        'ffmpeg',
        '-hwaccel', 'auto',
        '-hwaccel_device', '1',
        '-loglevel', 'error',
        '-i', video_path,
        '-vf', f"select='eq(pict_type,I)',scale=360:-1",
        '-vsync', 'vfr',
        '-q:v', '2',
        '-stats',
        os.path.join(output_dir, 'frame_%04d.jpg')
    ]
    
    print("使用显卡加速模式...")
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    if result.returncode != 0:
        raise RuntimeError("显卡加速失败，请检查显卡驱动和FFmpeg配置")
    
    # 获取最新关键帧文件名
    frames = sorted([f for f in os.listdir(output_dir) if f.startswith('frame_')])
    if frames:
        latest_frame = os.path.join(output_dir, frames[-1])
        print(f"\n检测到最新关键帧文件: {latest_frame}\n", flush=True)  # 强制刷新输出
        return latest_frame
    print("警告: 未在临时目录中找到任何关键帧文件")
    return None

def check_ollama_connection():
    """检查Ollama服务连接"""
    client = ollama.Client(host='http://localhost:11434')
    max_retries = 3
    for i in range(max_retries):
        client.list()  # 简单API调用测试连接
        return client

def analyze_frames(frame_paths, model_name=None, prompt=None):
    """使用ollama分析多帧图像(优化GPU版本)"""
    # 验证所有图片有效性
    for frame_path in frame_paths:
        with Image.open(frame_path) as img:
            img.verify()
    
    client = check_ollama_connection()
    
    if prompt is None:
        prompt = "这是5张连续的动漫视频截图，请尽可能简略描述这个片段的内容，必须使用中文返回结果，描述时请专注于画面中人物，环境，动作，忽略文字信息，保持简洁"
    
    if model_name is None:
        model_name = "llava"
        
    # 简化参数设置
    options = {
        'num_thread': 2
    }
    
    # 分批处理
    max_batch_size = 5
    responses = []
    for i in range(0, len(frame_paths), max_batch_size):
        batch = frame_paths[i:i+max_batch_size]
        
        response = client.generate(
            model=model_name,
            prompt=prompt,
            images=batch,
            options=options
        )
        responses.append(response['response'].strip())
            
    return " ".join(responses)

def generate_report(analyses, video_name):
    """生成简化报告"""
    # 创建固定名称的输出文件夹
    video_name_base = os.path.splitext(video_name)[0]
    output_dir = os.path.join('output', video_name_base)
    os.makedirs(output_dir, exist_ok=True)
    
    report = f"## {os.path.splitext(video_name)[0]}\n"
    report += "| 时间段 | 内容概述 |\n"
    report += "|--------|----------|\n"
    
    video_path = os.path.join('input/video_input', video_name)
    report_path = os.path.join(output_dir, 'report.txt')
    duration = float(subprocess.run([
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ], capture_output=True, text=True).stdout)
    
    segment_duration = duration / len(analyses)
    
    for i, desc in enumerate(analyses):
        start_seconds = i * segment_duration
        end_seconds = (i + 1) * segment_duration
        start_time = str(timedelta(seconds=start_seconds))  
        end_time = str(timedelta(seconds=end_seconds))
        time_range = f"{start_time}-{end_time}"
        report += f"| {time_range} | {desc} |\n"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return report_path

def main():
    
    # 读取配置文件
    prompt = None
    model_name = None
    max_concurrent = 2
    processing_interval = 1.0
    min_memory_mb = 1000
    
    if os.path.exists('src/config.json'):
        with open('src/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            prompt = config.get('prompt')
            model_name = config.get('model_name')
            max_concurrent = config.get('max_concurrent_frames', 2)
            processing_interval = config.get('processing_interval', 1.0)
            min_memory_mb = config.get('min_free_memory_mb', 1000)

    temp_dir = 'temp_frames'
    input_dir = 'input/video_input'
    
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"输入目录 {input_dir} 不存在")
        
    video_files = [f for f in os.listdir(input_dir) if f.endswith(('.mp4', '.mkv', '.avi', '.mov'))]
    if not video_files:
        raise FileNotFoundError(f"输入目录 {input_dir} 中没有找到视频文件")
    # 创建信号量控制并发
    semaphore = threading.Semaphore(max_concurrent)
    
    analyses = []
    for video_file in video_files:
        video_path = os.path.join(input_dir, video_file)
        extract_keyframes(video_path, temp_dir)
        
        frames = sorted(os.listdir(temp_dir))
        total_frames = len(frames)
        frame_groups = [frames[i:i+5] for i in range(0, len(frames), 5)]
        
        for group_idx, frame_group in enumerate(frame_groups):
            frame_paths = [os.path.join(temp_dir, frame) for frame in frame_group]
            # 显示清晰的进度信息
            print(f"\r[处理进度] 关键帧组 {group_idx+1}/{len(frame_groups)} - 当前处理: {', '.join(frame_group)}", end="", flush=True)
            
            # 获取信号量
            semaphore.acquire()
            
            desc = analyze_frames(frame_paths, model_name=model_name, prompt=prompt)

            
            analyses.append(desc)
            report_path = generate_report(analyses, video_file)
        

    print("清理临时文件...")
    if os.path.exists(temp_dir):
        for frame in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, frame))
        os.rmdir(temp_dir)

    # 自动运行AI分析处理器
    import ai_auto_processor
    ai_auto_processor.main()


if __name__ == '__main__':
    main()
