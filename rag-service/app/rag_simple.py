#!/usr/bin/env python3
"""
RAG Service - 支持 PDF 上传
"""

import os
import sys
import json
import uuid
import threading
from pathlib import Path
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# 配置
MODEL_PATH = "/data/models/qwen/Qwen2-0___5B"
BOOKS_DIR = "/data/books"

os.makedirs(BOOKS_DIR, exist_ok=True)

# 加载模型
print("🚀 加载 Qwen2-0.5B 模型...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, trust_remote_code=True, device_map="auto")
print("✅ 模型加载完成!")

app = Flask(__name__)
app.config['BOOKS_DIR'] = BOOKS_DIR

tasks = {}
documents = []

def load_documents():
    """加载文档"""
    global documents
    documents = []
    
    from pypdf import PdfReader
    
    for file in Path(BOOKS_DIR).iterdir():
        try:
            if file.suffix.lower() == '.pdf':
                reader = PdfReader(str(file))
                text = "\n".join([p.extract_text() for p in reader.pages])
            elif file.suffix.lower() in ['.txt', '.md']:
                text = file.read_text(encoding='utf-8')
            else:
                continue
            
            # 分块
            chunks = [text[i:i+1000] for i in range(0, len(text), 800)]
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    documents.append({"id": f"{file.name}_{i}", "source": file.name, "text": chunk})
            print(f"📖 {file.name}: {len(chunks)} 块")
        except Exception as e:
            print(f"❌ {file.name}: {e}")
    
    print(f"✅ 共 {len(documents)} 个文档块")

def generate_response(q, task_id):
    try:
        tasks[task_id]["status"] = "processing"
        
        # RAG 检索
        keywords = q.lower().split()
        relevant = []
        for doc in documents:
            score = sum(1 for kw in keywords if kw in doc["text"].lower())
            if score > 0:
                relevant.append((score, doc))
        relevant.sort(reverse=True, key=lambda x: x[0])
        context = "\n\n".join([d[1]["text"] for _, d in relevant[:3]])
        sources = [d[1]["source"] for _, d in relevant[:3]]
        
        # 生成
        prompt = f"基于上下文回答。\n\n上下文：{context}\n\n问题：{q}\n\n回答：" if context else q
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(**inputs, max_new_tokens=1024)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        if context:
            response = response[len(prompt):].strip()
        
        tasks[task_id] = {"status": "completed", "result": response, "sources": sources}
    except Exception as e:
        tasks[task_id] = {"status": "failed", "error": str(e)}

@app.route("/health")
def health():
    return jsonify({"status": "ok", "documents": len(documents)})

@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files['file']
    if file.filename:
        filepath = os.path.join(BOOKS_DIR, secure_filename(file.filename))
        file.save(filepath)
        load_documents()
    return jsonify({"message": "OK", "documents": len(documents)})

@app.route("/files")
def list_files():
    files = [{"name": f.name, "size": f.stat().st_size} for f in Path(BOOKS_DIR).iterdir()]
    return jsonify({"files": files})

@app.route("/chat", methods=["POST"])
def chat():
    q = request.json.get("question", "")
    if not q:
        return jsonify({"error": "question required"}), 400
    
    # RAG
    keywords = q.lower().split()
    relevant = []
    for doc in documents:
        score = sum(1 for kw in keywords if kw in doc["text"].lower())
        if score > 0:
            relevant.append((score, doc))
    relevant.sort(reverse=True, key=lambda x: x[0])
    context = "\n\n".join([d[1]["text"] for _, d in relevant[:3]])
    sources = [d[1]["source"] for _, d in relevant[:3]]
    
    prompt = f"基于上下文回答。\n\n上下文：{context}\n\n问题：{q}\n\n回答：" if context else q
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=512)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if context:
        response = response[len(prompt):].strip()
    
    return jsonify({"answer": response, "sources": sources})

@app.route("/chat/async", methods=["POST"])
def chat_async():
    q = request.json.get("question", "")
    if not q:
        return jsonify({"error": "question required"}), 400
    
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "pending", "question": q}
    
    thread = threading.Thread(target=generate_response, args=(q, task_id))
    thread.daemon = True
    thread.start()
    
    return jsonify({"task_id": task_id, "status": "pending"})

@app.route("/chat/task/<task_id>")
def get_task(task_id):
    if task_id not in tasks:
        return jsonify({"error": "not found"}), 404
    return jsonify(tasks[task_id])

@app.route("/reload", methods=["POST"])
def reload():
    load_documents()
    return jsonify({"count": len(documents)})

if __name__ == "__main__":
    load_documents()
    print(f"📁 文档目录: {BOOKS_DIR}")
    app.run(host="0.0.0.0", port=8000)
