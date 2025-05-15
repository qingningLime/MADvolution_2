import os
from openai import OpenAI
from datetime import datetime

def get_latest_folder(directory):
    """获取目录中最新的文件夹（按修改时间排序）"""
    try:
        folders = []
        for entry in os.scandir(directory):
            if entry.is_dir():
                mtime = entry.stat().st_mtime  # 使用修改时间而非创建时间
                folders.append((entry.path, mtime))
        
        if not folders:
            print(f"警告：目录 {directory} 中没有子文件夹")
            return None
        
        # 按修改时间排序并返回最新的文件夹
        folders.sort(key=lambda x: x[1], reverse=True)
        print(f"找到最新文件夹: {folders[0][0]}")
        return folders[0][0]
    except Exception as e:
        print(f"获取最新文件夹出错: {e}")
        return None

def get_files_from_folder(folder, count=2):
    """从文件夹中获取最新的两个文件（按修改时间排序）"""
    try:
        files = []
        for entry in os.scandir(folder):
            if entry.is_file():
                mtime = entry.stat().st_mtime
                files.append((entry.path, mtime))
        
        if not files:
            print(f"警告：文件夹 {folder} 中没有文件")
            return []
        
        # 按修改时间排序并返回最新的文件
        files.sort(key=lambda x: x[1], reverse=True)
        print(f"找到文件: {[f[0] for f in files[:count]]}")
        return [f[0] for f in files[:count]]
    except Exception as e:
        print(f"获取文件出错: {e}")
        return []

def read_file_content(filepath):
    """读取文件内容"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

import json

def load_config():
    """加载配置文件"""
    with open('src/config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def process_with_deepseek(config, content):
    """使用DeepSeek API处理内容"""
    client = OpenAI(api_key=config['ai_auto_processor']['api_key'], 
                  base_url=config['ai_auto_processor']['base_url'])
    
    # 从config获取用户提示模板
    user_prompt = config['ai_auto_processor']['prompts']['user_template'].format(content=content)
    
    response = client.chat.completions.create(
        model=config['ai_auto_processor']['model'],
        messages=[
            {"role": "system", "content": config['ai_auto_processor']['system_prompt']},
            {"role": "user", "content": user_prompt},
        ],
        stream=False
    )
    return response.choices[0].message.content

def generate_report():
    """生成分析报告"""
    config = load_config()
    ai_config = config['ai_auto_processor']
    
    # 1. 获取最新文件夹及其中的文件
    latest_folder = get_latest_folder(ai_config['output_dir'])
    if not latest_folder:
        print("错误：output目录中没有文件夹")
        return
    
    latest_files = get_files_from_folder(latest_folder, ai_config['max_files'])
    if len(latest_files) < ai_config['max_files']:
        print(f"错误：文件夹 {os.path.basename(latest_folder)} 中文件不足")
        return
    
    # 2. 读取文件内容
    content = ""
    for filepath in latest_files:
        content += f"\n\n=== 文件: {os.path.basename(filepath)} ===\n"
        content += read_file_content(filepath)
    
    # 3. 调用DeepSeek处理
    print("正在使用ai大模型处理内容...")
    analysis_result = process_with_deepseek(config, content)
    
    # 4. 生成报告文件 - 放在项目根目录的"ai视频设备报告"文件夹
    ai_report_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai视频识别报告")
    os.makedirs(ai_report_dir, exist_ok=True)
    
    folder_name = os.path.basename(latest_folder)  # 获取分析文件夹名称
    report_filename = f"{folder_name}_ai_report.txt"
    report_path = os.path.join(ai_report_dir, report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(analysis_result)
    
    print(f"分析报告已生成: {report_path}")

if __name__ == "__main__":
    config = load_config()
    generate_report()
