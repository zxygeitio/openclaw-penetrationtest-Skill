#!/usr/bin/env python3
"""
RAG Service - 完整版
支持文档上传、知识库问答、流式输出、异步处理
"""

import os
import sys
import json
import uuid
import threading
import time
from pathlib import Path
from typing import List, Dict, Optional
from flask import Flask, request, jsonify, Response, stream_with_context
from werkzeug.utils import secure_filename

# 加载模型
print("🚀 加载 Qwen2-0.5B 模型...")
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

MODEL_PATH = "/data/models/qwen/Qwen2-0___5B"
BOOKS_DIR = "/data/books"
VECTOR_STORE = "/data/vector_store"

# 确保目录存在
os.makedirs(BOOKS_DIR, exist_ok=True)
os.makedirs(VECTOR_STORE, exist_ok=True)

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH, 
        trust_remote_code=True,
        device_map="auto"
    )
    print("✅ 模型加载完成!")
except Exception as e:
    print(f"❌ 模型加载失败: {e}")
    sys.exit(1)

# Flask API
app = Flask(__name__)
app.config['BOOKS_DIR'] = BOOKS_DIR
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# 后台任务存储
tasks: Dict[str, dict] = {}
# 向量存储（简化版）
documents: List[dict] = []

# 文档处理
def load_documents():
    """加载书籍文档"""
    global documents
    documents = []
    
    # 动态导入 pypdf
    from pypdf import PdfReader
    
    for file in Path(BOOKS_DIR).iterdir():
        try:
            if file.suffix.lower() == '.pdf':
                # PDF 文件
                reader = PdfReader(str(file))
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            elif file.suffix.lower() in ['.txt', '.md']:
                # 文本文件
                text = file.read_text(encoding='utf-8')
            else:
                continue
            
            # 简单分块
            chunks = [text[i:i+1000] for i in range(0, len(text), 800)]
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    documents.append({
                        "id": f"{file.name}_{i}",
                        "source": file.name,
                        "text": chunk
                    })
            print(f"📖 加载: {file.name} ({len(chunks)} 块)")
            
        except Exception as e:
            print(f"❌ 加载失败 {file.name}: {e}")
    
    print(f"✅ 共加载 {len(documents)} 个文档块")

def generate_response(question: str, task_id: str, use_rag: bool = True):
    """后台生成任务"""
    try:
        tasks[task_id]["status"] = "processing"
        
        context = ""
        if use_rag and documents:
            # 简单的关键词匹配（简化版 RAG）
            keywords = question.lower().split()
            relevant_docs = []
            for doc in documents:
                score = sum(1 for kw in keywords if kw in doc["text"].lower())
                if score > 0:
                    relevant_docs.append((score, doc))
            
            relevant_docs.sort(reverse=True, key=lambda x: x[0])
            context = "\n\n".join([d[1]["text"] for _, d in relevant_docs[:3]])
        
        # 构建提示词
        if context:
            prompt = f"""基于以下上下文回答问题。如果上下文没有相关信息，请基于你的知识回答。

上下文：
{context}

问题：{question}

回答："""
        else:
            prompt = question
        
        # 生成回答
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=1024,
            temperature=0.7
        )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 去除提示词
        if prompt != question:
            response = response[len(prompt):].strip()
        
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = response
        tasks[task_id]["sources"] = [d[1]["source"] for _, d in relevant_docs[:3]] if use_rag and documents else []
        
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok", 
        "model": "qwen2-0.5b",
        "documents": len(documents)
    })

@app.route("/upload", methods=["POST"])
def upload_file():
    """上传文档"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(BOOKS_DIR, filename)
    file.save(filepath)
    
    # 重新加载文档
    load_documents()
    
    return jsonify({
        "message": "File uploaded",
        "filename": filename,
        "documents": len(documents)
    })

@app.route("/files", methods=["GET"])
def list_files():
    """列出已上传的文件"""
    files = []
    for f in Path(BOOKS_DIR).iterdir():
        files.append({
            "name": f.name,
            "size": f.stat().st_size,
            "modified": f.stat().st_mtime
        })
    return jsonify({"files": files})

@app.route("/chat", methods=["POST"])
def chat():
    """同步聊天（适合短问题）"""
    data = request.json
    question = data.get("question", "")
    use_rag = data.get("use_rag", True)
    
    if not question:
        return jsonify({"error": "question is required"}), 400
    
    context = ""
    if use_rag and documents:
        keywords = question.lower().split()
        relevant_docs = []
        for doc in documents:
            score = sum(1 for kw in keywords if kw in doc["text"].lower())
            if score > 0:
                relevant_docs.append((score, doc))
        
        relevant_docs.sort(reverse=True, key=lambda x: x[0])
        context = "\n\n".join([d[1]["text"] for _, d in relevant_docs[:3]])
        sources = [d[1]["source"] for _, d in relevant_docs[:3]]
    
    if context:
        prompt = f"""基于以下上下文回答问题。如果上下文没有相关信息，请基于你的知识回答。

上下文：
{context}

问题：{question}

回答："""
    else:
        prompt = question
    
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=512,
        temperature=0.7
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    if prompt != question:
        response = response[len(prompt):].strip()
    
    return jsonify({
        "answer": response,
        "question": question,
        "sources": sources if use_rag and documents else []
    })

@app.route("/chat/async", methods=["POST"])
def chat_async():
    """异步聊天（适合长问题）"""
    data = request.json
    question = data.get("question", "")
    use_rag = data.get("use_rag", True)
    
    if not question:
        return jsonify({"error": "question is required"}), 400
    
    # 创建任务
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "pending",
        "question": question,
        "result": None,
        "error": None,
        "sources": []
    }
    
    # 启动后台线程
    thread = threading.Thread(target=generate_response, args=(question, task_id, use_rag))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "task_id": task_id,
        "status": "pending",
        "message": "任务已提交，请使用 /chat/task/{task_id} 查询结果"
    })

@app.route("/chat/task/<task_id>", methods=["GET"])
def get_task(task_id):
    """查询异步任务结果"""
    if task_id not in tasks:
        return jsonify({"error": "task not found"}), 404
    
    task = tasks[task_id]
    return jsonify({
        "task_id": task_id,
        "status": task["status"],
        "result": task.get("result"),
        "sources": task.get("sources", []),
        "error": task.get("error")
    })

@app.route("/tasks", methods=["GET"])
def list_tasks():
    """列出所有任务"""
    return jsonify({"tasks": tasks})

@app.route("/reload", methods=["POST"])
def reload_documents():
    """重新加载文档"""
    load_documents()
    return jsonify({"message": "Documents reloaded", "count": len(documents)})

if __name__ == "__main__":
    # 启动时加载文档
    load_documents()
    
    print("🌐 启动 RAG API 服务...")
    print("📝 API 说明:")
    print("   /health        - 健康检查")
    print("   /upload        - 上传文档")
    print("   /files         - 列出文件")
    print("   /chat          - 聊天问答")
    print("   /chat/async   - 异步聊天")
    print("   /chat/task/{id} - 查询结果")
    print("   /reload       - 重新加载文档")
    print(f"📁 文档目录: {BOOKS_DIR}")
    
    app.run(host="0.0.0.0", port=8000)
