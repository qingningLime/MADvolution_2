
# MADvolution2_剪辑跃迁: 智能AI剪辑视频生成工具使用说明

## 一、项目概述
MADvolution_2 是一款基于AI技术的全自动MAD视频生成工具，支持从视频内容分析、音乐节奏解析到智能剪辑脚本生成、视频导出的全流程自动化。通过整合多模态模型（如Ollama视觉模型、DeepSeek语言模型）和音视频处理库（如FFmpeg、Librosa），实现了动漫视频的场景识别、音乐情感匹配及精准剪辑，大幅降低MAD创作门槛。


## 二、环境搭建指南

### 2.1 系统要求
| 系统类型       | 支持版本                 | 硬件建议（推荐）              |
|----------------|--------------------------|-----------------------------|
| Windows        | 10/11（64位）            | NVIDIA RTX 1650+/AMD RX 6600+，8GB内存(需CUDA或ROCM支持)   |
| Linux          | Ubuntu 20.04+/Debian 11+  | NVIDIA GPU（需安装CUDA 11.8+） |
| macOS          | Ventura 13+              | M1芯片+（部分功能受限）    |

### 2.2 必备软件安装

#### 2.2.1 基础依赖
- **Python 3.8+**  
  - Windows/Linux：通过[Python官网](https://www.python.org/)下载安装包，需勾选“Add Python to PATH”。  
  - macOS：通过Homebrew安装：  
    ```bash
    brew install python@3.10
    ```

- **FFmpeg**  
  - Windows：从[华为云镜像站](https://mirrors.huaweicloud.com/ffmpeg/releases/)或其他国内源下载`ffmpeg-latest-win64-gpl.zip`，解压后将`ffmpeg.exe`复制到`C:/Windows/System32`并配置环境变量。  
  - Linux：  
    ```bash
    sudo apt-get install ffmpeg
    ```  
  - macOS：  
    ```bash
    brew install ffmpeg
    ```

- **Ollama（AI模型运行环境）**  
  - **安装**：  
    - 所有平台：从[Ollama官网](https://ollama.ai/)下载安装包  
    - 或通过命令行安装：  
      ```bash
      curl -fsSL https://ollama.ai/install.sh | sh
      ```  
  - **配置**：  
    1. 启动Ollama服务：  
       ```bash
       ollama serve
       ```  
    2. 下载视觉模型（首次使用自动下载）：  
       ```bash
       ollama run minicpm-v
       ```  
    3. 确保`config.json`中的`base_url`设置为`http://localhost:11434`

- **GPU加速（可选但推荐）**  
  - **NVIDIA显卡**：需安装[CUDA Toolkit 11.8+](https://developer.nvidia.com/cuda-toolkit)及对应驱动，安装后重启。  
  - **AMD显卡**：需安装[ROCm 5.7+/HIP](https://docs.amd.com/)及对应驱动，安装后重启。

#### 2.2.2 Python依赖
- **通过脚本自动安装**：  
  ```bash
  cd src
  python install_deps.py  # 自动安装所有Python依赖（需联网）
  ```  
  - 若安装失败，可手动安装：  
    ```bash
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    ```

- **依赖说明**：  
  | 库名               | 用途                               |
  |--------------------|------------------------------------|
  | `ollama`           | 调用本地多模态模型（如LLaVA）      |
  | `openai`           | 调用DeepSeek等云端API             |
  | `librosa`          | 音乐特征提取（节拍、频谱分析）     |
  | `moviepy`          | 视频剪辑基础库                     |
  | `faiss-gpu`        | 向量检索（需CUDA或rocm环境）             |
  | `PyQt5`            | GUI界面开发（暂未完全启用）        |


## 三、文件配置详解

### 3.1 核心配置文件 `config.json`
路径：`src/config.json`  
**需用户手动配置的关键参数**：

#### 3.1.1 Ollama本地模型配置（图像分析）
```json
"ollama": {
  "base_url": "http://localhost:11434",  // Ollama服务地址，需提前启动Ollama客户端
  "embedding_model": "shaw/dmeta-embedding-zh",  // 中文图像Embedding模型（默认已适配）
  "model_name": "minicpm-v"  // 多模态模型名称（支持minicpm-v、llava等）
}
```
- **启动Ollama服务**：  
  1. 下载并安装[Ollama](https://ollama.ai/)。  
  2. 启动命令行：  
     ```bash
     ollama run minicpm-v  # 加载视觉模型（首次运行会自动下载，约4GB）
     ```

#### 3.1.2 DeepSeek云端API配置（语言分析）
```json
"ai_auto_processor": {
  "api_key": "your-deepseek-api-key",  // 需在DeepSeek官网申请
  "base_url": "https://api.deepseek.com",  // 官方API地址
  "model": "deepseek-chat"  // 使用的语言模型（支持deepseek-chat、gpt-4等）
}
```
- **获取API密钥**：  
  1. 注册[DeepSeek账号](https://deepseek.com/account/signup)。  
  2. 在“控制台-API密钥”页面创建新密钥，填入此处。

#### 3.1.3 分析参数配置
```json
"prompt": "这是动漫视频某片段的5张连续截图...",  // 图像分析提示词（控制输出格式，建议保留默认）
"max_concurrent_frames": 1,  // 并发分析帧数（GPU显存不足时调小，如1）
"processing_interval": 2.0,  // 处理间隔（秒，避免API频率限制）
"rag": {
  "chunk_size": 1000,  // 文本分块大小（用于长文本分析）
  "top_k": 3  // 检索返回结果数
}
```


### 3.2 其他配置文件
- **音乐分析配置**：`src/music_config.py`  
  可调整音频采样率、节拍检测敏感度等参数，一般无需修改。  
- **提示词模板**：`mad剪辑提示词/`目录  
  - `系统提示词.txt`：核心分析逻辑提示词，修改可能影响结果准确性。  
  - `提示词.txt`：用户可自定义剪辑风格（如“添加赛博朋克滤镜”“加快副歌部分节奏”）。


## 四、操作流程指南

### 4.1 输入文件准备
#### 4.1.1 目录结构说明

##### 输入目录结构 (input/)
```
input/
├── music_input/        # [必填]背景音乐目录
│   └── *.flac/.mp3     # 支持FLAC/MP3格式，中文文件名
│                       # 要求：单首音乐，与视频风格匹配
│
├── video_input/        # [选填]单视频处理目录
│   └── 视频名.mkv      # 推荐MKV/MP4格式，分辨率≥1080p
│                       # 支持内嵌字幕，自动识别时间轴
│
└── 视频批处理/         # [选填]批量视频处理目录
    ├── 视频/           # 存放多集视频文件
    │   └── 第01集.mkv  # 命名需包含集数(如"第01集")
    │
    └── 字幕/           # [可选]对应字幕文件
        └── 第01集.ass  # 需与视频文件同名
```

##### 输出目录结构
```
output/                # 视频分析临时文件
├── 视频名/            # 每部视频单独目录
│   ├── frames/        # 提取的关键帧
│   └── report.txt     # 场景分析报告
│
output_Music/          # 音乐分析结果
│   └── 故事板.json    # 节拍/歌词时间轴

最终输出视频/          # 成品视频
└── 歌曲名/           # 按音乐分类
    └── 歌曲名_final.mp4  # 最终视频文件
```

##### AI工作目录
```
ai分析数据/            # 分析报告汇总
├── Music_report.md    # 音乐情感分析
└── combined_reports.md # 合并报告

ai剪辑脚本/            # 生成的剪辑脚本
└── mad_script.md      # 时间轴/画面/歌词匹配

ai切割素材/            # 视频片段缓存
└── mad_script/        # 按脚本生成的片段
```

#### 4.1.2 文件要求
- **视频文件**：  
  - 单文件处理：放置于`video_input/`，支持MP4/MKV/AVI等格式，建议分辨率≥1080p。  
  - 批量处理：在`视频批处理/视频`中放置多个视频，系统自动按集数匹配字幕（需将字幕放入`视频批处理/字幕`）。  
- **背景音乐**：仅支持单首音乐，需与视频风格匹配（如热血音乐对应战斗场景）。


### 4.2 运行步骤（以单文件为例）

#### 4.2.1 第一步：视频内容分析
```bash
# 命令行运行
python src/video_analyzer.py

# 或通过GUI启动（推荐）
python src/main_gui.py  # 点击“视频批量分析工具”按钮
```
- **执行逻辑**：  
  1. 提取视频关键帧（每5秒1帧，GPU加速）。  
  2. 调用Ollama模型分析画面内容，生成`output/视频名/report.txt`。  
  3. 自动识别字幕（若有），生成时间轴文件。

#### 4.2.2 第二步：音乐特征分析
```bash
python src/music_analyzer.py
```
- **执行逻辑**：  
  1. 解析音乐节拍、频谱，生成`output_Music/故事板.json`。  
  2. 分析歌词情感，生成`ai分析数据/Music_report.md`。

#### 4.2.3 第三步：生成剪辑脚本
```bash
python src/mad_script_generator.py
```
- **交互说明**：  
  输入剪辑需求（如“制作燃向MAD，重点突出战斗画面”），按提示输入`q`结束。  
- **输出结果**：  
  `ai剪辑脚本/mad_script.md`，包含时间轴、歌词匹配、画面描述三列。

#### 4.2.4 第四步：自动化剪辑
```bash
# 切割视频片段
python src/auto_cut_video.py

# 合并片段并添加音乐
python src/video_merger.py
```
- **结果存储**：  
  最终视频存于`最终输出视频/歌曲名/歌曲名_final.mp4`，支持二次剪辑。


### 4.3 批量处理流程（高级功能）
```bash
python src/batch_video_processor.py
```
- **适用场景**：处理多集动漫（如番剧第1-12集）。  
- **操作要点**：  
  1. 在`视频批处理/视频`中放置多集MKV文件，命名格式需包含集数（如`第01集.mkv`）。  
  2. 字幕文件需与视频同名（如`第01集.ass`），放置于`视频批处理/字幕`。  
  3. 系统自动按集分析，生成合并后的长视频脚本。


## 五、工具链使用说明

### 5.1 缓存清理工具
```bash
python src/clear_cache.py
```
- **功能**：一键删除以下目录内容：  
  - `output/`：临时分析文件  
  - `temp_frames/`：视频帧缓存  
  - `ai切割素材/`：旧版本切割片段  
- **建议频率**：每次完成剪辑后执行，释放存储空间。

### 5.2 报告合并工具
```bash
python src/combine_reports.py
```
- **功能**：  
  1. 合并`ai视频识别报告/`下的所有.txt文件为`ai分析数据/combined_reports.md`。  
  2. 自动按时间顺序排列，添加章节分隔符。


## 六、常见问题与解决方案

### 6.1 模型调用失败
- **现象**：`video_analyzer.py`报错“无法连接到Ollama服务”。  
- **解决**：  
  1. 确保Ollama客户端已启动，且`config.json`中的`base_url`正确。  
  2. 检查防火墙设置，允许本地端口`11434`通信。

### 6.2 剪辑脚本内容混乱
- **现象**：生成的脚本时间轴跳跃或画面与歌词不匹配。  
- **解决**：  
  1. 调整`config.json`中的`prompt`提示词，明确需求（如“优先选择人物特写画面”）。  
  2. 在`mad剪辑提示词/提示词.txt`中添加更具体的规则（如“副歌部分使用快节奏剪辑”）。

### 6.3 视频导出失败
- **现象**：`video_merger.py`报错“找不到视频片段”。  
- **解决**：  
  1. 确认`ai切割素材/`目录下存在按脚本生成的MP4片段。  
  2. 检查FFmpeg路径是否正确（可重新运行`install_deps.py`修复）。


## 七、进阶技巧

### 7.1 自定义模型
- **更换视觉模型**：  
  在Ollama中运行其他支持图像的模型（如`ollama run llava`），并修改`config.json`的`model_name`为`llava`。  
- **使用本地大语言模型**：  
  替换`ai_auto_processor.model`为本地部署的模型（如LLaMA-2），需自行配置服务地址。

### 7.2 高级剪辑控制
- **调整脚本格式**：  
  在`mad_script.md`中手动修改时间轴（格式需保持Markdown表格），重新运行`auto_cut_video.py`。  
- **添加转场特效**：  
  在`video_merger.py`中修改FFmpeg参数（如添加`-vf "fade=type=out:st=0:d=2"`），详见[FFmpeg转场文档](https://ffmpeg.org/ffmpeg-filters.html#fade)。


## 八、贡献与反馈
- **代码贡献**：  
  1. Fork本仓库，创建新分支（如`feature/add-new-model`）。  
  2. 提交PR时需包含测试用例及文档更新。  
- **问题反馈**：  
  在GitHub Issues中提交模板：  
  ```
  [BUG/功能请求] 标题  
  环境：Windows 11 + Python 3.10  
  描述：执行xxx步骤时报错xxx  
  复现步骤：1. ... 2. ...  
  截图/日志：（如有）  
  ```


## 九、许可证与声明

### MIT 许可证

版权所有 (c) 2025 MADvolution_2 开发者Lime

特此免费授予任何获得本软件及相关文档文件（以下简称"软件"）副本的人无限制使用软件的权利，包括但不限于使用、复制、修改、合并、发布、分发、再许可和/或出售软件副本的权利，并允许向其提供软件的人这样做，但须符合以下条件：

上述版权声明和本许可声明应包含在软件的所有副本或重要部分中。

本软件按"原样"提供，不提供任何明示或暗示的担保，包括但不限于对适销性、特定用途适用性和非侵权性的担保。在任何情况下，作者或版权持有人均不对任何索赔、损害或其他责任负责，无论是在合同、侵权或其他行为中产生的，还是与软件或软件的使用或其他交易相关的。

### 免责声明
1. 请仅用于合法用途，禁止传播侵权内容。
2. 开发者不对因使用本工具导致的任何法律纠纷负责。

 

**获取最新版本**：https://github.com/qingningLime/MADvolution_2  
**联系我们**：qq：3447131904 

---
**感谢使用MADvolution_2！🌟** 如需帮助，请随时提交Issue或邮件联系我们。
