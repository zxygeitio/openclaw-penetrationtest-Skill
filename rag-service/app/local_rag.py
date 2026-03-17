#!/usr/bin/env python3
"""
RAG Service - 本地模型版本
支持流式输出和后台任务
"""

import os
import sys
import json
import uuid
import threading
from pathlib import Path
from typing import List, Dict
from flask import Flask, request, jsonify, Response, stream_with_context
from werkzeug.serving import make_server

# 加载模型
print("🚀 加载 Qwen2-0.5B 模型...")
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

MODEL_PATH = "/data/models/qwen/Qwen2-0___5B"

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

# 后台任务存储
tasks: Dict[str, dict] = {}

def generate_response(question: str, task_id: str):
    """后台生成任务"""
    try:
        tasks[task_id]["status"] = "processing"
        
        inputs = tokenizer(question, return_tensors="pt").to(model.device)
        
        # 流式生成
        outputs = model.generate(
            **inputs,
            max_new_tokens=1024,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["result"] = response
        
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": "qwen2-0.5b"})

@app.route("/chat", methods=["POST"])
def chat():
    """同步聊天（适合短问题）"""
    data = request.json
    question = data.get("question", "")
    
    if not question:
        return jsonify({"error": "question is required"}), 400
    
    inputs = tokenizer(question, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=512,
        temperature=0.7,
        top_p=0.9
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return jsonify({
        "answer": response,
        "question": question
    })

@app.route("/chat/stream", methods=["POST"])
def chat_stream():
    """流式聊天（边生成边返回）"""
    data = request.json
    question = data.get("question", "")
    
    if not question:
        return jsonify({"error": "question is required"}), 400
    
    def generate():
        try:
            inputs = tokenizer(question, return_tensors="pt").to(model.device)
            
            # 流式生成
            generated_ids = []
            for outputs in model.generate(
                **inputs,
                max_new_tokens=1024,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                stream=True  # 启用流式
            ):
                # 这里简化处理，实际需要更好的流式支持
                text = tokenizer.decode(outputs, skip_special_tokens=True)
                yield f"data: {json.dumps({'text': text})}\n\n"
            
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(
        stream_with_context(generate()),
        content_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

@app.route("/chat/async", methods=["POST"])
def chat_async():
    """异步聊天（后台处理，适合长问题）"""
    data = request.json
    question = data.get("question", "")
    
    if not question:
        return jsonify({"error": "question is required"}), 400
    
    # 创建任务
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "pending",
        "question": question,
        "result": None,
        "error": None
    }
    
    # 启动后台线程
    thread = threading.Thread(target=generate_response, args=(question, task_id))
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
        "error": task.get("error")
    })

@app.route("/embed", methods=["POST"])
def embed():
    """生成文本嵌入向量"""
    data = request.json
    texts = data.get("texts", [])
    
    if not texts:
        return jsonify({"error": "texts is required"}), 400
    
    # 首次使用时加载嵌入模型
    if not hasattr(embed, "embedding_model"):
        print("📥 加载嵌入模型...")
        from sentence_transformers import SentenceTransformer
        embed.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    embeddings = embed.embedding_model.encode(texts).tolist()
    
    return jsonify({"embeddings": embeddings})

if __name__ == "__main__":
    print("🌐 启动 RAG API 服务...")
    print("📝 API 说明:")
    print("   /health         - 健康检查")
    print("   /chat           - 同步聊天（短问题）")
    print("   /chat/stream    - 流式聊天")
    print("   /chat/async    - 异步聊天（长问题）")
    print("   /chat/task/{id} - 查询异步任务")
    print("   /embed          - 文本嵌入")
    app.run(host="0.0.0.0", port=8000)
