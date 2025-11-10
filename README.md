# 东方财富融资融券数据可视化

## 项目简介
本项目是一个股票融资融券数据可视化工具，通过东方财富API获取历史数据，并提供直观的图表展示和数据查询功能。

## 功能特性
- 实时获取股票融资融券历史数据
- 图表可视化展示融资余额、融券余额和收盘价走势
- 数据表格展示详细的历史记录
- 支持按股票代码搜索和按日期范围筛选
- 支持本地和公网访问

## 技术栈
- 前端：HTML5, CSS3, JavaScript, Chart.js
- 后端：Python Flask
- API：东方财富Choice数据接口
- 公网访问：cpolar

## 一键启动服务

### 本地Windows环境

#### 前置条件
- 安装Python 3.6+
- 安装cpolar并完成登录配置
- 安装所需Python库：`pip install flask brotli requests flask-cors`

#### 使用方法

##### 启动服务（推荐）
1. 在命令提示符(cmd)中以管理员身份运行：`python start_all.py`
2. 系统会自动：
   - 启动后端API服务（默认端口5000）
   - 启动前端HTTP服务（默认端口8000）
   - 配置cpolar公开前后端服务

3. 访问方式：
   - 本地访问：http://localhost:8000
   - 公网访问：通过cpolar控制台查看（http://localhost:9200）

4. 命令行参数：
   ```
   python start_all.py [选项]
   
   选项：
     --backend-port PORT   # 设置后端服务端口，默认5000
     --frontend-port PORT  # 设置前端服务端口，默认8000
     --no-cpolar           # 不启动cpolar服务
   ```

##### 停止服务
1. 常规停止（会关闭所有Python进程）：`python stop_all.py`
2. 优雅停止（只关闭服务窗口，不终止其他Python程序）：`python stop_all.py --graceful`
3. 系统会自动关闭相关进程和窗口

### Trae AI环境（在线开发环境）

由于Trae AI环境的限制，多窗口操作可能无法正常工作。请使用以下简化步骤：

1. 启动后端服务：
   ```bash
   cd api
   python margin-trading.py
   ```

2. 在另一个终端中启动前端服务：
   ```bash
   python -m http.server 8000
   ```

3. 使用Trae AI的预览功能访问前端页面

注意：在Trae AI环境中，cpolar公网访问功能可能无法使用，建议在本地Windows环境中使用完整功能

## 注意事项
- 首次使用前请确保Python环境配置正确
- cpolar配置成功后，可以通过公网URL访问您的应用
- 保持start-all.bat启动的窗口开启以维持服务运行
- 详细日志保存在logs目录下

## 常见问题
- 如果启动失败，请检查logs目录下的日志文件获取详细错误信息
- cpolar免费版有流量限制，请注意合理使用
- 如需自定义端口，请修改批处理文件中的相应配置