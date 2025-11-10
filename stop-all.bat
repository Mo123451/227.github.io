@echo off

:: 设置标题
TITLE 一键停止前后端服务与cpolar

:: 检查是否以管理员权限运行
NET SESSION >nul 2>&1
if %errorLevel% neq 0 (
    echo 请以管理员权限运行此批处理文件！
    pause
    exit /b 1
)

echo ====================================
echo 一键停止前后端服务与cpolar
echo ====================================

:: 停止所有相关Python进程
echo 正在停止Python服务进程...
taskkill /f /im python.exe /t >nul 2>&1

:: 停止cpolar进程
echo 正在停止cpolar进程...
taskkill /f /im cpolar.exe /t >nul 2>&1

:: 关闭相关的cmd窗口
echo 正在关闭相关命令窗口...
taskkill /f /fi "WINDOWTITLE eq 后端服务" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq 前端服务" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq cpolar前端" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq cpolar后端" >nul 2>&1
echo ====================================
echo 所有服务已停止！
echo - Python进程已终止
echo - cpolar进程已终止
echo - 相关命令窗口已关闭
echo 注意：
echo 1. 可能会关闭您正在运行的其他Python程序
echo 2. 如果服务未完全停止，请手动检查任务管理器
echo ====================================
pause