import os
import json
from datetime import datetime
from openai import OpenAI

class MadScriptGenerator:
    def __init__(self):
        self.config = self.load_config()
        self.client = OpenAI(
            api_key=self.config['api_key'],
            base_url=self.config['base_url']
        )
        self.output_dir = "ai剪辑脚本"
        os.makedirs(self.output_dir, exist_ok=True)

    def load_config(self):
        """加载配置文件"""
        with open('src/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return {
            'api_key': config['ai_auto_processor']['api_key'],
            'base_url': config['ai_auto_processor']['base_url'],
            'model': config['ai_auto_processor']['model']
        }

    def load_prompts(self):
        """加载系统提示词和用户提示词"""
        prompt_dir = "mad剪辑提示词"
        system_prompt_path = os.path.join(prompt_dir, "系统提示词.txt")
        user_prompt_path = os.path.join(prompt_dir, "提示词.txt")
        
        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
        
        with open(user_prompt_path, 'r', encoding='utf-8') as f:
            user_prompt_template = f.read()
            
        return system_prompt, user_prompt_template

    def load_content(self):
        """加载ai分析数据内容"""
        content_dir = "ai分析数据"
        content = ""
        file_count = 0
        
        print("\n正在加载分析数据...")
        for filename in sorted(os.listdir(content_dir)):
            filepath = os.path.join(content_dir, filename)
            if os.path.isfile(filepath) and not filename.startswith('.'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    file_content = f.read().strip()
                    if file_content:
                        content += f"\n\n=== 分析数据文件: {filename} ===\n{file_content}"
                        file_count += 1
        
        print(f"已加载 {file_count} 个分析数据文件")
        if not content:
            print("警告: 未加载任何有效分析数据")
        return content

    def get_user_input(self):
        """获取用户终端输入"""
        print("\n请输入您的剪辑需求(输入q退出):")
        user_input = input("> ")
        if user_input.lower() == 'q':
            return None
        return user_input

    def call_deepseek(self, system_prompt, user_prompt):
        """调用Deepseek API"""
        response = self.client.chat.completions.create(
            model=self.config['model'],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=False
        )
        return response.choices[0].message.content

    def save_result(self, result):
        """保存结果到MD文件，覆盖已有文件"""
        filename = "mad_script.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"\n结果已保存到: {filepath} (覆盖原有内容)")

    def run(self):
        """主运行流程"""
        print("=== MAD剪辑脚本生成器 ===")
        
        # 加载提示词和内容
        system_prompt, user_prompt_template = self.load_prompts()
        content = self.load_content()
        
        while True:
            # 获取用户输入
            user_input = self.get_user_input()
            if user_input is None:
                break
                
            # 构建完整提示词并确保使用分析数据
            full_prompt = f"""根据以下分析数据和用户需求生成剪辑脚本：
            
            【分析数据内容】
            {content}
            
            【用户需求】
            {user_input}

            【格式要求】
            | 时间段 | 歌词内容 | 集数+时间码 | 画面对应的内容 |
            |--------|----------|-----------------------|----------|
            | 00:00-00:02 | 天空没有极限 - 邓紫棋 | 第1集 00:00.31~00:02.31 | 祥子冒雨来见CRYCHIC成员 |
            | 00:02-00:15 | [间奏] | 第1集 02:05.00~02:17.00 | 立希愤怒质问祥子 |
            
            【具体要求】
            1. 必须基于上述分析数据生成脚本
            2. 每个镜头选择必须引用具体分析数据
            3. 保持原有输出格式
            4. 确保时间轴连贯性"""
            
            # 调用API
            print("\n正在生成剪辑脚本...")
            result = self.call_deepseek(system_prompt, full_prompt)
            
            # 输出结果
            print("\n=== 生成的剪辑脚本 ===")
            print(result)
            
            # 保存结果
            self.save_result(result)

if __name__ == "__main__":
    generator = MadScriptGenerator()
    generator.run()
