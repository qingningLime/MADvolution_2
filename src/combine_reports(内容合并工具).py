import os
from natsort import natsorted

def combine_reports(input_dir, output_file):
    """
    将指定目录下的所有报告文件合并为一个Markdown文件
    
    参数:
        input_dir: 包含报告文件的目录路径
        output_file: 输出的Markdown文件路径
    """
    # 获取目录下所有.txt文件并按自然顺序排序
    report_files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]
    sorted_files = natsorted(report_files)
    
    with open(output_file, 'w', encoding='utf-8') as md_file:
        for filename in sorted_files:
            filepath = os.path.join(input_dir, filename)
            
            # 添加文件标题作为Markdown二级标题
            title = os.path.splitext(filename)[0]
            md_file.write(f"## {title}\n\n")
            
            # 写入文件内容
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                md_file.write(content)
            
            # 添加分隔符
            md_file.write("\n\n---\n\n")

def cleanup_files(input_dir, output_folder):
    """删除输入和输出目录中的文件"""
    # 删除原始报告文件
    print("\n即将删除以下文件:")
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        print(f"- {file_path}")
    
    # 删除output文件夹内容
    if os.path.exists(output_folder):
        for item in os.listdir(output_folder):
            item_path = os.path.join(output_folder, item)
            print(f"- {item_path}")
    
    confirm = input("\n确认要删除以上文件吗？(y/n): ").lower()
    if confirm != 'y':
        print("取消删除操作")
        return
    
    # 执行删除操作
    print("\n开始删除文件...")
    deleted_count = 0
    
    # 删除原始报告文件
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
                print(f"已删除: {file_path}")
                deleted_count += 1
        except Exception as e:
            print(f"删除文件{file_path}时出错: {e}")
    
    # 删除output文件夹内容
    if os.path.exists(output_folder):
        for item in os.listdir(output_folder):
            item_path = os.path.join(output_folder, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    print(f"已删除目录: {item_path}")
                    deleted_count += 1
                else:
                    os.unlink(item_path)
                    print(f"已删除文件: {item_path}")
                    deleted_count += 1
            except Exception as e:
                print(f"删除{item_path}时出错: {e}")
    
    print(f"\n删除完成，共删除 {deleted_count} 个文件/目录")

if __name__ == "__main__":
    input_dir = "ai视频识别报告"
    output_dir = "ai分析数据"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "combined_reports.md")
    combine_reports(input_dir, output_file)
    print(f"报告已合并保存到 {output_file}")
    
    import shutil
    output_folder = "output"
    cleanup_files(input_dir, output_folder)
