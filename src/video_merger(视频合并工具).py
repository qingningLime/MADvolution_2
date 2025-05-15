import os
import subprocess
from pathlib import Path

def extract_song_name(audio_path):
    """从音频文件名中提取歌曲名（去掉序号和歌手）"""
    stem = audio_path.stem
    return stem.split('-')[-1].strip()

def get_video_clips():
    """获取ai切割的视频片段"""
    clips_dir = Path("ai切割素材/mad_script")
    video_files = list(clips_dir.glob("*.mp4"))
    if not video_files:
        raise FileNotFoundError(f"未找到任何视频片段，请检查目录：{clips_dir}")
    return sorted(video_files, key=lambda x: int(x.stem.split('_')[0]))

def get_music_file():
    """获取音乐文件"""
    music_dir = Path("input/music_input")
    music_files = list(music_dir.glob("*.flac")) + list(music_dir.glob("*.mp3"))
    if not music_files:
        raise FileNotFoundError(f"未找到任何音乐文件，请检查目录：{music_dir}")
    return music_files[0]  # 使用第一个音乐文件

def merge_videos(video_files, output_dir):
    """合并视频片段"""
    list_file = output_dir / "concat_list.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for file in video_files:
            f.write(f"file '{file.resolve()}'\n")

    merged_video = output_dir / "merged.mp4"
    subprocess.run([
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(merged_video)
    ], check=True)
    list_file.unlink()
    return merged_video

def add_music(video_file, audio_file, output_file):
    """添加背景音乐并调整音频"""
    subprocess.run([
        "ffmpeg",
        "-i", str(video_file),
        "-i", str(audio_file),
        "-filter_complex",
        "[1:a]volume=0.8,adelay=0:all=1,afade=t=in:st=0:d=2[bgm]",
        "-map", "0:v",
        "-map", "[bgm]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_file)
    ], check=True)

def main():
    try:
        video_files = get_video_clips()
        audio_file = get_music_file()
        song_name = extract_song_name(audio_file)
        
        output_dir = Path("最终输出视频") / song_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"找到 {len(video_files)} 个视频片段，音乐：{audio_file.name}")
        
        # 合并视频
        merged_video = merge_videos(video_files, output_dir)
        
        # 获取音乐时长
        probe = subprocess.run([
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_file)
        ], capture_output=True, text=True, check=True)
        music_duration = float(probe.stdout.strip())
        
        # 截取与音乐等长的视频
        trimmed_video = output_dir / "trimmed.mp4"
        subprocess.run([
            "ffmpeg",
            "-i", str(merged_video),
            "-t", str(music_duration),
            "-c", "copy",
            str(trimmed_video)
        ], check=True)
        
        # 添加音乐
        final_output = output_dir / f"{song_name}_final.mp4"
        add_music(trimmed_video, audio_file, final_output)
        
        # 清理临时文件
        merged_video.unlink(missing_ok=True)
        trimmed_video.unlink(missing_ok=True)
        
        print(f"视频合并完成！保存至：{final_output}")
        
    except Exception as e:
        print(f"处理失败：{str(e)}")

if __name__ == "__main__":
    main()
