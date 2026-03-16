FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# 复制应用代码
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# 创建数据目录
RUN mkdir -p /data/books /data/chroma

# 暴露端口
EXPOSE 8000 11434

# 启动命令
CMD ["sh", "-c", "ollama serve &> /var/log/ollama.log & \
     sleep 5 && \
     ollama pull qwen2:0.5b && \
     ollama pull nomic-embed-text && \
     python main.py"]
