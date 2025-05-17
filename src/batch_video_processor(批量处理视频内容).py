import os
import re
import shutil
import glob
import subprocess
import json
from pathlib import Path
from datetime import datetime

from difflib import SequenceMatcher

def find_matching_subtitle(video_file, subtitle_dir):
    """智能匹配最佳字幕文件"""
    # 提取视频文件关键信息
    video_name = os.path.splitext(video_file)[0]
    ep_num = re.search(r'\[(\d{2})\]', video_name)
    ep_num = ep_num.group(1) if ep_num else None
    
    # 获取所有候选字幕文件
    candidates = [f for f in os.listdir(subtitle_dir) 
                if f.endswith('.ass')]
    
    if not candidates:
        print(f"未找到任何候选字幕文件")
        return None
    
    # 计算每个候选文件的匹配分数
    scores = []
    for sub in candidates:
        score = 0
        
        # 集数匹配(50分)
        if ep_num and f"[{ep_num}]" in sub:
            score += 50
        
        # 名称相似度(30分)
        video_key = re.sub(r'\[.*?\]', '', video_name).strip().lower()
        sub_key = re.sub(r'\[.*?\]', '', sub).strip().lower()
        score += int(30 * SequenceMatcher(
            None, video_key, sub_key).ratio())
        
        # 扩展名匹配(20分)
        if '.scjp.ass' in sub:
            score += 20
            
        scores.append(score)
        print(f"字幕 '{sub}' 匹配分数: {score}")  # 调试输出
    
    # 返回最佳匹配
    best_idx = scores.index(max(scores))
    best_match = candidates[best_idx]
    print(f"选择最佳匹配字幕: {best_match} (分数: {max(scores)})")
    return os.path.join(subtitle_dir, best_match)

def check_analysis_success(video_filename):
    """检查是否生成分析文档"""
    # 移除视频文件扩展名
    base_name = os.path.splitext(video_filename)[0]
    report_path = os.path.join('ai视频识别报告', f"{base_name}_ai_report.txt")
    print(f"正在检查报告文件: {report_path}")
    if os.path.exists(report_path):
        size = os.path.getsize(report_path)
        print(f"报告文件大小: {size} bytes")
        return size > 0
    return False

def init_log(batch_id):
    """初始化日志文件"""
    log_dir = os.path.join('input', '视频批处理', '批处理日志')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f'batch_{batch_id}.json')
    return log_path

def save_log(log_path, data):
    """保存日志"""
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_log(log_path):
    """加载日志"""
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def clean_temp_frames():
    """清理残留的临时帧目录"""
    temp_dir = 'temp_frames'
    if os.path.exists(temp_dir):
        for frame in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, frame))
        os.rmdir(temp_dir)
        print(f"已清理残留临时目录: {temp_dir}")

def process_batch(video_dir, subtitle_dir, output_dir, batch_size=1, log_path=None):
    """处理一批视频文件"""
    print(f"视频目录: {video_dir}")
    print(f"字幕目录: {subtitle_dir}")
    print(f"输出目录: {output_dir}")
    
    video_files = sorted([f for f in os.listdir(video_dir) if f.endswith('.mkv')])
    print(f"找到视频文件: {video_files}")

    # 初始化日志数据
    log_data = {
        'batch_id': datetime.now().strftime("%Y%m%d_%H%M%S"),
        'videos': []
    }
    
    # 加载已有日志（恢复处理时）
    if log_path and os.path.exists(log_path):
        log_data = load_log(log_path)
        print(f"从日志恢复处理: {log_path}")

    for i in range(0, len(video_files), batch_size):
        batch = video_files[i:i+batch_size]
        
        for video in batch:
            # 检查是否已处理过
            processed = next((v for v in log_data['videos'] if v['filename'] == video), None)
            if processed and processed['status'] == 'completed':
                print(f"跳过已处理的视频: {video}")
                continue
                
            # 清空输出目录
            for f in os.listdir(output_dir):
                os.remove(os.path.join(output_dir, f))
            
            # 清理临时文件
            clean_temp_frames()
            
            # 更新日志状态为处理中
            video_log = {
                'filename': video,
                'status': 'processing',
                'start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'end_time': None,
                'error': None
            }
            if not processed:
                log_data['videos'].append(video_log)
            else:
                processed.update(video_log)
            save_log(log_path, log_data)
                
            video_path = os.path.join(video_dir, video)
            subtitle_path = find_matching_subtitle(video, subtitle_dir)
            
            if subtitle_path:
                # 1. 拷贝文件到处理目录
                shutil.copy2(video_path, output_dir)
                shutil.copy2(subtitle_path, output_dir)
                print(f"已拷贝: {video} 和匹配的字幕")
            
                # 2. 执行视频分析
                print("正在执行video_analyzer.py...")
                import video_analyzer
                video_analyzer.main()
                
                # 3. 检查分析结果
                if check_analysis_success(video):
                    print(f"视频 {video} 分析完成，清理输入目录")
                    for f in os.listdir(output_dir):
                        os.remove(os.path.join(output_dir, f))
                        
                    # 更新日志状态为完成
                    video_log['status'] = 'completed'
                    video_log['end_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_log(log_path, log_data)
                else:
                    print(f"警告: 视频 {video} 分析文档未生成")
                    video_log['status'] = 'failed'
                    video_log['error'] = '分析文档未生成'
                    save_log(log_path, log_data)
                    return False
                clean_temp_frames()
            else:
                print(f"警告: 未找到 {video} 的字幕文件")
                return False
                
    return True

if __name__ == "__main__":
    # 配置路径
    VIDEO_DIR = os.path.join('input', '视频批处理', '视频')
    SUBTITLE_DIR = os.path.join('input', '视频批处理', '字幕') 
    OUTPUT_DIR = os.path.join('input', 'video_input')
    
    # 创建输出目录(如果不存在)
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    # 清理可能残留的临时文件
    clean_temp_frames()
    
    # 初始化日志
    batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = init_log(batch_id)
    
    # 检查是否有未完成的日志
    latest_log = max(glob.glob(os.path.join('input', '视频批处理', '批处理日志', 'batch_*.json')), default=None)
    
    # 每次处理1个视频(可调整batch_size)
    success = process_batch(
        VIDEO_DIR, 
        SUBTITLE_DIR, 
        OUTPUT_DIR, 
        batch_size=1,
        log_path=latest_log if latest_log else log_path
    )
    
    # 全部完成后删除日志
    if success and log_path and os.path.exists(log_path):
        os.remove(log_path)
        print("所有视频处理完成，已清除日志文件")
