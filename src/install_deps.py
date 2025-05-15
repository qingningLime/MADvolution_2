#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
from typing import Tuple

# 配置国内镜像源
PYPI_MIRROR = "https://pypi.tuna.tsinghua.edu.cn/simple"
FFMPEG_WINDOWS_URL = "https://mirrors.huaweicloud.com/ffmpeg/releases/ffmpeg-latest-win64-gpl.zip"

def check_python_version() -> bool:
    """检查Python版本是否>=3.8"""
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        return False
    return True

def run_command(cmd: str, admin: bool = False) -> Tuple[bool, str]:
    """运行系统命令"""
    try:
        if admin and platform.system() == "Windows":
            cmd = f"powershell Start-Process -Verb RunAs -Wait -FilePath cmd -ArgumentList '/c {cmd}'"
        result = subprocess.run(cmd, shell=True, check=True, 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_ffmpeg() -> bool:
    """检查FFmpeg是否安装"""
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_ffmpeg() -> bool:
    """安装FFmpeg"""
    print("正在安装FFmpeg...")
    system = platform.system()
    
    if system == "Windows":
        # Windows下下载并安装FFmpeg
        success, output = run_command(
            f"curl -LO {FFMPEG_WINDOWS_URL} && "
            "tar -xf ffmpeg-latest-win64-gpl.zip && "
            "move ffmpeg-latest-win64-gpl/bin/ffmpeg.exe C:/Windows/System32/",
            admin=True
        )
    elif system in ["Linux", "Darwin"]:
        # Linux/Mac使用包管理器
        if system == "Linux":
            success, output = run_command("sudo apt-get install -y ffmpeg", admin=True)
        else:  # Darwin (Mac)
            success, output = run_command("brew install ffmpeg", admin=True)
    else:
        print(f"不支持的系统: {system}")
        return False
    
    if success:
        print("FFmpeg安装成功")
        return True
    else:
        print(f"FFmpeg安装失败: {output}")
        return False

def check_cuda() -> bool:
    """检查CUDA环境"""
    try:
        subprocess.run(["nvcc", "--version"], check=True,
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_python_deps() -> bool:
    """安装Python依赖"""
    print("正在安装Python依赖...")
    
    # 替换requirements.txt中的faiss-cpu为faiss-gpu(如果CUDA可用)
    requirements_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    with open(requirements_file, "r") as f:
        requirements = f.read()
    
    if check_cuda():
        requirements = requirements.replace("faiss-cpu>=", "faiss-gpu>=")
    
    # 写入临时文件
    temp_req = os.path.join(os.path.dirname(__file__), "temp_requirements.txt")
    with open(temp_req, "w") as f:
        f.write(requirements)
    
    # 使用国内镜像源安装
    cmd = f"python -m pip install -r {temp_req} -i {PYPI_MIRROR}"
    success, output = run_command(cmd)
    
    # 删除临时文件
    os.remove(temp_req)
    
    if success:
        print("Python依赖安装成功")
        return True
    else:
        print(f"Python依赖安装失败: {output}")
        return False

def generate_report() -> dict:
    """生成安装报告"""
    report = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "ffmpeg_installed": check_ffmpeg(),
        "cuda_available": check_cuda(),
        "system": platform.system(),
    }
    return report

def main():
    print("=== MADvolution 依赖安装程序 ===")
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 检查并安装FFmpeg
    if not check_ffmpeg():
        if not install_ffmpeg():
            sys.exit(1)
    
    # 安装Python依赖
    if not install_python_deps():
        sys.exit(1)
    
    # 生成报告
    report = generate_report()
    print("\n=== 安装报告 ===")
    print(f"系统: {report['system']}")
    print(f"Python版本: {report['python_version']}")
    print(f"FFmpeg已安装: {'是' if report['ffmpeg_installed'] else '否'}")
    print(f"CUDA可用: {'是' if report['cuda_available'] else '否'}")
    
    print("\n所有依赖安装完成！")

if __name__ == "__main__":
    main()
