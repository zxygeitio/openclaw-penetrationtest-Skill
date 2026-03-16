#!/usr/bin/env python3
"""
RAG Service with Ollama + LangChain + Chroma
安全知识问答服务
"""

import os
import json
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# LangChain + Ollama
from langchain_community.llms import Ollama
from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader, DirectoryLoader
)
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# 配置
DATA_DIR = "/data/books"
CHROMA_DIR = "/data/chroma"
MODEL_NAME = "qwen2:0.5b"  # 小模型，CPU 可跑
EMBED_MODEL = "nomic-embed-text"

app = FastAPI(title="Security RAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
llm = None
qa_chain = None
vectorstore = None

class QueryRequest(BaseModel):
    question: str
    history: Optional[List[dict]] = None

class QueryResponse(BaseModel)
    answer: str
    sources: List[str]

def init_system():
    """初始化系统"""
    global llm, qa_chain, vectorstore
    
    print("🔧 初始化 Ollama...")
    llm = Ollama(model=MODEL_NAME)
    
    print("🔧 初始化 Embeddings...")
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    
    # 检查向量库是否存在
    chroma_path = Path(CHROMA_DIR)
    if chroma_path.exists() and any(chroma_path.iterdir()):
        print("📚 加载已有向量库...")
        vectorstore = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings
        )
    else:
        print("⚠️ 向量库不存在，请先上传书籍并运行 /rebuild")
        return
    
    # 创建 QA 链
    prompt_template = """你是一个专业的网络安全助手，基于给定的上下文回答问题。

上下文：
{context}

问题：{question}

请用中文回答，如果上下文中没有相关信息，请说明找不到答案。"""

    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": PROMPT}
    )
    
    print("✅ 系统初始化完成!")

def rebuild_index():
    """重建向量索引"""
    global vectorstore, qa_chain
    
    print("🔧 初始化 Embeddings...")
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    
    # 加载文档
    documents = []
    data_path = Path(DATA_DIR)
    
    if not data_path.exists():
        raise HTTPException(status_code=400, detail="数据目录不存在")
    
    # PDF 文件
    for pdf_file in data_path.glob("*.pdf"):
        print(f"📄 加载 PDF: {pdf_file.name}")
        try:
            loader = PyPDFLoader(str(pdf_file))
            docs = loader.load()
            documents.extend(docs)
        except Exception as e:
            print(f"❌ 加载 {pdf_file.name} 失败: {e}")
    
    # TXT 文件
    for txt_file in data_path.glob("*.txt"):
        print(f"📄 加载 TXT: {txt_file.name}")
        try:
            loader = TextLoader(str(txt_file), encoding="utf-8")
            docs = loader.load()
            documents.extend(docs)
        except Exception as e:
            print(f"❌ 加载 {txt_file.name} 失败: {e}")
    
    if not documents:
        raise HTTPException(status_code=400, detail="未找到任何文档")
    
    # 分块
    print(f"📝 分块文档 ({len(documents)} 个文档)...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    texts = text_splitter.split_documents(documents)
    print(f"✂️ 分块完成: {len(texts)} 个块")
    
    # 创建向量库
    print("🗄️ 创建向量库...")
    vectorstore = Chroma.from_documents(
        documents=texts,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )
    
    # 创建 QA 链
    prompt_template = """你是一个专业的网络安全助手，基于给定的上下文回答问题。

上下文：
{context}

问题：{question}

请用中文回答，如果上下文中没有相关信息，请说明找不到答案。"""

    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": PROMPT}
    )
    
    print("✅ 向量库重建完成!")

@app.on_event("startup")
async def startup():
    try:
        init_system()
    except Exception as e:
        print(f"⚠️ 初始化警告: {e}")

@app.get("/")
async def root():
    return {"status": "ok", "message": "Security RAG API 运行中"}

@app.get("/health")
async def health():
    return {"status": "healthy", "model": MODEL_NAME}

@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    if not qa_chain:
        raise HTTPException(status_code=503, detail="系统未初始化")
    
    try:
        result = qa_chain.invoke(req.question)
        answer = result.get("result", str(result))
        
        # 获取源文档
        sources = []
        if vectorstore:
            docs = vectorstore.similarity_search(req.question, k=2)
            sources = [d.metadata.get("source", "unknown") for d in docs]
        
        return QueryResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rebuild")
async def rebuild():
    """重建向量索引"""
    try:
        rebuild_index()
        return {"status": "ok", "message": "向量库重建完成"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def stats():
    """获取统计信息"""
    if not vectorstore:
        return {"documents": 0, "status": "not_initialized"}
    
    try:
        count = vectorstore._collection.count()
        return {"documents": count, "status": "ready"}
    except:
        return {"documents": 0, "status": "ready"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
