#!/bin/bash

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
# .\venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 创建必要的目录
mkdir -p uploads

# 创建环境变量文件（如果不存在）
if [ ! -f .env ]; then
    cp .env.example .env
    echo "请编辑 .env 文件并设置必要的环境变量"
fi 