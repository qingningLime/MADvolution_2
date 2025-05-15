# 音乐分析配置文件
from pathlib import Path

# 基础路径配置
INPUT_DIR = Path("input/music_input")
OUTPUT_DIR = Path("output_Music")

# 支持的文件格式
AUDIO_EXTENSIONS = ['.mp3', '.flac', '.wav', '.m4a']
LYRIC_EXTENSIONS = ['.lrc', '.txt']

# 音频分析参数
DEFAULT_SAMPLE_RATE = 22050  # 音频采样率(Hz)
BEAT_TIGHTNESS = 100         # 节拍检测敏感度
INTERLUDE_THRESHOLD = 0.2    # 间奏检测能量阈值(0-1)

# 歌词处理配置
FILTER_KEYWORDS = [
    '作词', '作曲', '编曲', '制作人', '制作', '录音', '混音', '母带',
    'Produced', 'Recorded', 'Mixed', 'Mastered', 'Arranged',
    'by：', '：', '@', 'OP/SP', 'Production', 'Company'
]  # 要过滤的非歌词内容

# 输出配置
STORYBOARD_FORMATS = ['json', 'md']  # 生成的故事板格式
