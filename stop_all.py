
import os
import subprocess
import time
import argparse
import logging

# 配置日志
log_dir = os.path.join(os.getcwd(), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'shutdown.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

print("=" * 50)
print("      一键停止前后端服务与cpolar")
print("=" * 50)

# 解析命令行参数
parser = argparse.ArgumentParser(description='一键停止前后端服务与cpolar')
parser.add_argument('--graceful', action='store_true', help='优雅关闭（不会强制终止所有Python进程）')
args = parser.parse_args()

if args.graceful:
    # 优雅关闭模式：只关闭相关窗口，不终止所有Python进程
    print("优雅关闭模式：只关闭相关窗口...")
    logger.info("开始优雅关闭服务")
    
    # 关闭相关的cmd窗口
    print("正在关闭相关命令窗口...")
    windows_to_close = ["后端服务", "前端服务", "cpolar前端", "cpolar后端"]
    closed_windows = 0
    
    for window in windows_to_close:
        try:
            result = subprocess.run(['taskkill', '/f', '/fi', f'WINDOWTITLE eq {window}'], 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                print(f"✓ 已关闭窗口: {window}")
                logger.info(f"已关闭窗口: {window}")
                closed_windows += 1
        except Exception as e:
            logger.error(f"关闭窗口 {window} 时出错: {str(e)}")
    
    # 尝试停止cpolar进程
    print("正在停止cpolar进程...")
    try:
        subprocess.run(['taskkill', '/f', '/im', 'cpolar.exe', '/t'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✓ cpolar进程已终止")
        logger.info("cpolar进程已终止")
    except Exception as e:
        logger.error(f"停止cpolar进程时出错: {str(e)}")
        print(f"✗ 停止cpolar进程时出错: {str(e)}")
    
    print(f"✓ 已关闭 {closed_windows} 个相关命令窗口")

else:
    # 强制关闭模式（默认）：终止所有相关进程
    print("强制关闭模式：终止所有相关进程...")
    logger.info("开始强制关闭服务")
    
    # 停止所有相关Python进程
    print("正在停止Python服务进程...")
    try:
        subprocess.run(['taskkill', '/f', '/im', 'python.exe', '/t'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✓ Python进程已终止")
        logger.info("Python进程已终止")
    except Exception as e:
        logger.error(f"停止Python进程时出错: {str(e)}")
        print(f"✗ 停止Python进程时出错: {str(e)}")
    
    # 停止cpolar进程
    print("正在停止cpolar进程...")
    try:
        subprocess.run(['taskkill', '/f', '/im', 'cpolar.exe', '/t'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✓ cpolar进程已终止")
        logger.info("cpolar进程已终止")
    except Exception as e:
        logger.error(f"停止cpolar进程时出错: {str(e)}")
        print(f"✗ 停止cpolar进程时出错: {str(e)}")
    
    # 关闭相关的cmd窗口
    print("正在关闭相关命令窗口...")
    windows_to_close = ["后端服务", "前端服务", "cpolar前端", "cpolar后端"]
    for window in windows_to_close:
        try:
            subprocess.run(['taskkill', '/f', '/fi', f'WINDOWTITLE eq {window}'], 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            logger.error(f"关闭窗口 {window} 时出错: {str(e)}")
    print("✓ 相关命令窗口已关闭")
    logger.info("相关命令窗口已关闭")

print("
" + "=" * 50)
print("      所有服务已停止！")
if args.graceful:
    print("- 相关命令窗口已关闭")
    print("- cpolar进程已终止")
    print("注意：")
    print("1. 未终止其他Python进程，只关闭了服务窗口")
    print("2. 如果服务未完全停止，请手动检查任务管理器")
else:
    print("- Python进程已终止")
    print("- cpolar进程已终止")
    print("- 相关命令窗口已关闭")
    print("注意：")
    print("1. 可能会关闭您正在运行的其他Python程序")
    print("2. 使用 --graceful 参数可以只关闭服务窗口而不终止所有Python进程")
    print("3. 如果服务未完全停止，请手动检查任务管理器")
print("=" * 50)

print("按回车键退出...")
input()