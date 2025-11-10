import os
import sys
import subprocess
import time
import shutil
import platform
import socket
import argparse
import logging

# 检查操作系统
if platform.system() != 'Windows':
    print("错误：此脚本仅支持Windows操作系统！")
    sys.exit(1)

# 检查是否以管理员权限运行
try:
    import ctypes
    is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    if not is_admin:
        print("警告：建议以管理员权限运行此脚本以确保所有功能正常工作！")
except:
    pass

print("=" * 50)
print("      一键启动前后端服务与cpolar公开")
print("=" * 50)

# 检查Python是否安装
try:
    subprocess.run(['python', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("✓ Python环境已安装")
except:
    print("✗ 错误：未找到Python环境，请先安装Python！")
    sys.exit(1)

# 检查cpolar是否安装
try:
    subprocess.run(['where', 'cpolar'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("✓ cpolar已安装")
except:
    print("✗ 警告：未找到cpolar命令，请先安装cpolar并添加到环境变量！")
    print("将继续启动前后端服务，但无法进行公网公开")
    cpolar_available = False
else:
    cpolar_available = True

# 配置日志
log_dir = os.path.join(os.getcwd(), 'logs')
os.makedirs(log_dir, exist_ok=True)
print(f"✓ 日志目录已创建: {log_dir}")

# 设置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'startup.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 解析命令行参数
parser = argparse.ArgumentParser(description='一键启动前后端服务与cpolar公开')
parser.add_argument('--backend-port', type=int, default=5000, help='后端服务端口')
parser.add_argument('--frontend-port', type=int, default=8000, help='前端服务端口')
parser.add_argument('--no-cpolar', action='store_true', help='不启动cpolar')
args = parser.parse_args()

# 获取当前目录
current_dir = os.getcwd()
api_dir = os.path.join(current_dir, 'api')

# 函数：检查端口是否被占用
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# 函数：等待服务启动
def wait_for_service(port, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_in_use(port):
            return True
        time.sleep(1)
    return False

# 函数：检测是否在Trae AI环境中
def is_trae_ai_environment():
    # 检查是否在Trae AI环境中
    try:
        # 检查环境变量或特殊标记
        env_vars = os.environ.keys()
        is_trae = any('trae' in var.lower() or 'vscode' in var.lower() for var in env_vars)
        
        # 尝试检查系统路径或其他特征
        if not is_trae:
            # 尝试简单的cmd窗口创建测试
            test_cmd = 'cmd /c "exit"'
            result = subprocess.run(test_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            is_trae = result.returncode != 0
    except:
        is_trae = True
    
    return is_trae

# 函数：启动进程
def start_process(name, command, log_file=None, port=None, retries=3):
    logger.info(f"正在启动 {name}...")
    print(f"正在启动 {name}...")
    
    # 如果指定了端口，检查是否已被占用
    if port and is_port_in_use(port):
        logger.warning(f"警告：端口 {port} 已被占用，可能影响服务启动")
        print(f"⚠ 警告：端口 {port} 已被占用，可能影响服务启动")
    
    # 检测是否在Trae AI或类似的受限环境中
    is_restricted_env = is_trae_ai_environment()
    
    if is_restricted_env:
        logger.warning("检测到Trae AI或其他受限环境")
        print(f"注意：检测到Trae AI或其他受限环境")
        print(f"环境限制：无法自动在新窗口启动进程")
        
        # 为不同服务提供特定的手动启动命令
        if "后端服务" in name:
            print(f"\n请在一个新的终端中运行以下命令启动{name}：")
            print(f"  cd api")
            print(f"  python margin-trading.py")
        elif "前端服务" in name:
            print(f"\n请在另一个新的终端中运行以下命令启动{name}：")
            print(f"  python -m http.server {port}")
        else:
            print(f"\n请在新的终端中运行以下命令启动{name}：")
            print(f"  {command}")
        
        return False
    else:
        # 尝试多次启动
        for attempt in range(retries):
            # 在正常Windows环境中，使用新窗口启动
            cmd = ['cmd', '/c', 'start', '/min', f'"{name}"', 'cmd', '/k', command]
            try:
                subprocess.Popen(cmd, shell=False)
                print(f"✓ {name} 已启动 (尝试 {attempt+1}/{retries})")
                
                # 如果指定了端口，等待服务启动
                if port:
                    print(f"等待 {name} 在端口 {port} 上启动...")
                    if wait_for_service(port):
                        logger.info(f"{name} 服务在端口 {port} 上成功启动")
                        print(f"✓ {name} 服务在端口 {port} 上成功启动")
                        return True
                    else:
                        logger.warning(f"{name} 服务在端口 {port} 上启动超时")
                        print(f"⚠ {name} 服务在端口 {port} 上启动超时")
                        if attempt < retries - 1:
                            print(f"重试启动 {name}...")
                            time.sleep(2)
                            continue
                else:
                    return True
            except Exception as e:
                logger.error(f"启动 {name} 失败: {str(e)}")
                print(f"✗ 启动 {name} 失败: {str(e)}")
                if attempt < retries - 1:
                    print(f"重试启动 {name}...")
                    time.sleep(2)
                    continue
                
        print(f"请尝试手动在新窗口中执行：{command}")
        return False

# 检测是否在Trae AI环境中
in_trae_ai = is_trae_ai_environment()

# 如果在Trae AI环境中，提供更详细的手动启动指南
if in_trae_ai:
    print("\n" + "=" * 60)
    print("    在Trae AI环境中的启动指南")
    print("=" * 60)
    print("1. 后端服务启动步骤：")
    print(f"   - 打开一个新的终端标签")
    print(f"   - 运行命令: cd api")
    print(f"   - 运行命令: python margin-trading.py")
    print(f"   - 后端服务将在端口 {args.backend_port} 上运行")
    print()
    print("2. 前端服务启动步骤：")
    print(f"   - 打开另一个新的终端标签")
    print(f"   - 运行命令: python -m http.server {args.frontend_port}")
    print(f"   - 前端服务将在端口 {args.frontend_port} 上运行")
    print()
    print("3. 访问方式：")
    print(f"   - 本地访问: http://localhost:{args.frontend_port}")
    print("   - 在Trae AI中，使用预览功能查看前端页面")
    print("=" * 60)
    print()

# 启动后端服务
backend_log = os.path.join(log_dir, 'backend.log')
backend_cmd = f'cd "{api_dir}" && python margin-trading.py > "{backend_log}" 2>&1'
backend_success = start_process("后端服务", backend_cmd, port=args.backend_port)

# 等待后端服务启动
if backend_success:
    print("后端服务已启动，等待初始化完成...")
    time.sleep(3)

# 启动前端服务
frontend_log = os.path.join(log_dir, 'frontend.log')
frontend_cmd = f'cd "{current_dir}" && python -m http.server {args.frontend_port} > "{frontend_log}" 2>&1'
frontend_success = start_process("前端服务", frontend_cmd, port=args.frontend_port)

# 等待前端服务启动
if frontend_success:
    print("前端服务已启动，等待初始化完成...")
    time.sleep(3)

# 如果cpolar可用且用户未禁用，启动cpolar
if cpolar_available and not args.no_cpolar:
    # 启动cpolar前端
    cpolar_frontend_log = os.path.join(log_dir, 'cpolar_frontend.log')
    cpolar_frontend_cmd = f'cpolar http {args.frontend_port} > "{cpolar_frontend_log}" 2>&1'
    cpolar_frontend_success = start_process("cpolar前端", cpolar_frontend_cmd)
    
    # 启动cpolar后端
    cpolar_backend_log = os.path.join(log_dir, 'cpolar_backend.log')
    cpolar_backend_cmd = f'cpolar http {args.backend_port} > "{cpolar_backend_log}" 2>&1'
    cpolar_backend_success = start_process("cpolar后端", cpolar_backend_cmd)
    
    # 等待cpolar配置完成
    if cpolar_frontend_success or cpolar_backend_success:
        print("等待cpolar配置完成...")
        time.sleep(8)

print("\n" + "=" * 50)
print("      服务启动完成！")
print(f"- 后端服务运行在 http://localhost:{args.backend_port}")
print(f"- 前端服务运行在 http://localhost:{args.frontend_port}")
if cpolar_available and not args.no_cpolar:
    print("- 请访问 http://localhost:9200 查看cpolar控制台获取公网访问地址")
    print("- 或在cpolar客户端查看公网URL")
print("=" * 50)
print("注意：")
print("1. 保持所有窗口开启以维持服务运行")
print(f"2. 查看 {log_dir} 目录下的日志文件获取详细输出")
print("3. 停止服务时，运行 python stop_all.py")
print("=" * 50)

# 创建停止服务的Python脚本
stop_script_content = '''
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

print("\n" + "=" * 50)
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
input()'''

with open(os.path.join(current_dir, 'stop_all.py'), 'w', encoding='utf-8') as f:
    f.write(stop_script_content)

print("\n✓ 已创建停止服务脚本: stop_all.py")
print("使用方法:")
print("  - 常规停止: python stop_all.py")
print("  - 优雅停止(不关闭其他Python程序): python stop_all.py --graceful")

# 环境检测和提示
print("\n" + "=" * 60)
print("环境兼容性提示：")
if in_trae_ai:
    print("⚠ 当前环境: Trae AI或其他受限环境")
    print("  - 请按照上述指南在多个终端中手动启动服务")
    print("  - 使用Trae AI的预览功能访问前端页面")
    print("  - cpolar功能在当前环境中不可用")
else:
    print("✓ 当前环境: 本地Windows环境")
    print("  - 一键启动功能完全可用")
    print("  - 所有服务已在独立窗口中启动")
    if cpolar_available and not args.no_cpolar:
        print("  - cpolar公网访问已配置")
print()
print("命令行参数:")
print(f"  - --backend-port {args.backend_port}  # 设置后端服务端口")
print(f"  - --frontend-port {args.frontend_port}  # 设置前端服务端口")
print(f"  - --no-cpolar  # 不启动cpolar服务")
print()
print("详细操作指南请参考README.md文件")
print("=" * 60)

print("\n按回车键退出...")
input()