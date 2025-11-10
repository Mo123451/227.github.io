@echo off

:: 设置标题
TITLE 一键启动前后端服务与cpolar公开

:: 检查是否以管理员权限运行
NET SESSION >nul 2>&1
if %errorLevel% neq 0 (
    echo 请以管理员权限运行此批处理文件！
    pause
    exit /b 1
)

echo ====================================
echo 一键启动前后端服务与cpolar公开
echo ====================================

:: 检查Python是否安装
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo 未找到Python环境，请先安装Python！
    pause
    exit /b 1
)

:: 检查cpolar是否安装
where cpolar >nul 2>&1
if %errorLevel% neq 0 (
    echo 未找到cpolar命令，请先安装cpolar并添加到环境变量！
    pause
    exit /b 1
)

:: 创建输出目录
mkdir logs 2>nul

:: 启动后端服务（在新窗口中）
echo 正在启动后端服务...
start "后端服务" cmd /k "cd api && python margin-trading.py > ../logs/backend.log 2>&1"

:: 等待后端服务启动
echo 等待后端服务启动...
ping -n 5 127.0.0.1 >nul

:: 启动前端HTTP服务（在新窗口中）
echo 正在启动前端HTTP服务...
start "前端服务" cmd /k "python -m http.server 8000 > logs/frontend.log 2>&1"

:: 等待前端服务启动
echo 等待前端服务启动...
ping -n 5 127.0.0.1 >nul

:: 使用cpolar公开8000端口（前端）
echo 正在配置cpolar公开前端网站...
start "cpolar前端" cmd /k "cpolar http 8000 > logs/cpolar_frontend.log 2>&1"

:: 使用cpolar公开5000端口（后端）
echo 正在配置cpolar公开后端API...
start "cpolar后端" cmd /k "cpolar http 5000 > logs/cpolar_backend.log 2>&1"

:: 等待cpolar配置完成
echo 等待cpolar配置完成...
ping -n 8 127.0.0.1 >nul

:: 显示信息
echo ====================================
echo 服务启动完成！
echo - 后端服务运行在 http://localhost:5000
echo - 前端服务运行在 http://localhost:8000
echo - 请访问 http://localhost:9200 查看cpolar控制台获取公网访问地址
echo - 或在cpolar客户端查看公网URL
echo ====================================
echo 注意：
echo 1. 保持所有窗口开启以维持服务运行
echo 2. 查看logs目录下的日志文件获取详细输出
echo 3. 停止服务时，关闭所有命令窗口即可
echo ====================================