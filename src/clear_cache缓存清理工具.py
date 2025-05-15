import os
import shutil

def clear_directory_contents(dir_path):
    """递归删除目录中所有文件和空子目录"""
    file_count = 0
    
    # 首先删除所有文件
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                os.remove(file_path)
                file_count += 1
            except Exception as e:
                print(f"无法删除文件 {file_path}: {str(e)}")
    
    # 然后删除空目录(从最深层开始)
    for root, dirs, files in os.walk(dir_path, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                os.rmdir(dir_path)
                print(f"已删除空目录: {dir_path}")
            except OSError:
                # 目录非空时会抛出异常，此时跳过
                pass
    
    return file_count

def main():
    print("=== 缓存清理工具 ===")
    print("请选择要清理的目录：")
    print("1. ai视频识别报告")
    print("2. output目录")
    print("3. input/video_input")
    print("4. 最终输出视频")
    print("5. ai切割素材")
    print("6. 全部清理")
    
    choice = input("请输入选项(1/2/3/4/5/6): ").strip()
    
    targets = []
    if choice == '1':
        targets.append('ai视频识别报告')
    elif choice == '2':
        targets.append('output')
    elif choice == '3':
        targets.append('input/video_input')
    elif choice == '4':
        targets.append('最终输出视频')
    elif choice == '5':
        targets.append('ai切割素材')
    elif choice == '6':
        targets.extend(['ai视频识别报告', 'output', 'input/video_input', '最终输出视频', 'ai切割素材'])
    else:
        print("无效选项，程序退出")
        return
    
    # 统计总文件数
    total_files = 0
    for target in targets:
        if os.path.exists(target):
            for root, dirs, files in os.walk(target):
                total_files += len(files)
    
    if total_files == 0:
        print("没有找到可清理的文件")
        return
    
    print(f"\n将要删除 {total_files} 个文件")
    confirm = input("确认要执行此操作吗？(y/n): ").strip().lower()
    if confirm != 'y':
        print("操作已取消")
        return
    
    # 执行清理
    print("\n开始清理...")
    cleared_files = 0
    for target in targets:
        if os.path.exists(target):
            print(f"正在清理 {target} 目录...")
            cleared = clear_directory_contents(target)
            cleared_files += cleared
            print(f"已删除 {cleared} 个文件")
        else:
            print(f"目录 {target} 不存在，跳过")
    
    print(f"\n操作完成，共删除 {cleared_files}/{total_files} 个文件")

if __name__ == "__main__":
    main()
