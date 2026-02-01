#!/bin/bash
# MultiDatabase GUI 启动脚本
# 双击此文件即可启动图形界面

# 获取脚本所在目录
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 切换到项目目录
cd "$DIR"

# 检查并安装依赖
echo "正在检查依赖..."
if ! python3 -c "import customtkinter" 2>/dev/null; then
    echo "首次运行，正在安装 CustomTkinter..."
    pip3 install customtkinter || pip3 install --break-system-packages customtkinter
    echo "安装完成！"
fi

# 启动GUI
echo "正在启动 MultiDatabase GUI..."
python3 gui_app.py
