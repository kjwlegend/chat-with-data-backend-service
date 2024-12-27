#!/bin/bash

# 启动 Redis
docker-compose up -d

# 安装依赖
pip install -r requirements.txt

# 启动应用
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 