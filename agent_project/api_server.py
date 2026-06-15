from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sys
import os
import time
import json

# 添加agent_project目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 使用绝对导入而非相对导入
from agent.react_agent import ReactAgent
from rag.vector_store import VectorStoreService
from utils.logger_handler import logger
from utils.redis_handler import (
    redis_client, redis_available, redis_conf,
    chat_history_key, agent_reply_cache_key,
    clear_all_llm_cache,
)
from utils.metrics import metrics

app = FastAPI(title="租房智能客服API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化Agent实例
agent_instance = ReactAgent()

# 初始化向量存储服务
vector_store_service = VectorStoreService()

# Redis对话历史配置
CHAT_HISTORY_TTL = redis_conf.get("chat_history_ttl", 86400)
CHAT_HISTORY_MAX_LEN = redis_conf.get("chat_history_max_len", 50)
AGENT_REPLY_TTL = redis_conf.get("agent_reply_ttl", 1800)

# 文件上传目录
UPLOAD_DIR = os.path.join(project_root, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str
    success: bool = True


class ChatHistory(BaseModel):
    """聊天记录模型"""
    role: str
    content: str


class ChatHistoryResponse(BaseModel):
    """对话历史响应模型"""
    session_id: str
    messages: List[ChatHistory]
    success: bool = True


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    filename: str
    message: str
    success: bool = True


@app.get("/")
async def root():
    """API根路径"""
    return {"message": "租房智能客服API运行中", "status": "ok"}


@app.post("/app/agent/chat", response_model=ChatResponse)
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    智能客服聊天接口
    :param request: 聊天请求
    :return: 聊天响应
    """
    t_start = time.perf_counter()
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="消息不能为空")
        
        session_id = request.session_id or "default"
        history_key = chat_history_key(session_id)
        
        # 保存用户消息到Redis历史
        if redis_available:
            redis_client.rpush(history_key, json.dumps({
                "role": "user",
                "content": request.message
            }))
        
        # 尝试Agent回复缓存命中
        reply_key = agent_reply_cache_key(request.message)
        cached_reply = None
        if redis_available:
            try:
                cached_reply = redis_client.get(reply_key)
                if cached_reply:
                    logger.info(f"[Agent缓存] 命中缓存: {request.message[:30]}...")
                    metrics.incr_agent_cache_hit()
                else:
                    metrics.incr_agent_cache_miss()
            except Exception as e:
                logger.warning(f"[Agent缓存] Redis读取异常,降级走Agent: {e}")
                metrics.incr_agent_cache_miss()
        else:
            metrics.incr_agent_cache_miss()
        
        if cached_reply:
            full_response = cached_reply
        else:
            # 调用Agent获取回复
            response_messages = []
            res_stream = agent_instance.execute_stream(request.message)
            
            # 收集流式响应
            for chunk in res_stream:
                response_messages.append(chunk)
            
            full_response = "".join(response_messages).strip()
            
            # 写入Agent回复缓存
            if redis_available:
                try:
                    redis_client.setex(reply_key, AGENT_REPLY_TTL, full_response)
                    logger.info(f"[Agent缓存] 回复已缓存, TTL={AGENT_REPLY_TTL}s")
                except Exception as e:
                    logger.warning(f"[Agent缓存] Redis写入异常: {e}")
        
        # 保存助手回复到Redis历史
        if redis_available:
            redis_client.rpush(history_key, json.dumps({
                "role": "assistant",
                "content": full_response
            }))
            redis_client.expire(history_key, CHAT_HISTORY_TTL)
            redis_client.ltrim(history_key, -CHAT_HISTORY_MAX_LEN, -1)
        
        elapsed_ms = (time.perf_counter() - t_start) * 1000
        metrics.incr_api(success=True, elapsed_ms=elapsed_ms)
        
        return ChatResponse(
            response=full_response,
            success=True
        )
    
    except Exception as e:
        logger.error(f"[聊天接口]处理请求失败: {str(e)}")
        elapsed_ms = (time.perf_counter() - t_start) * 1000
        metrics.incr_api(success=False, elapsed_ms=elapsed_ms)
        return ChatResponse(
            response=f"抱歉,处理您的问题时出现了错误: {str(e)}",
            success=False
        )


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    智能客服流式聊天接口(Server-Sent Events)
    :param request: 聊天请求
    :return: 流式响应
    """
    metrics.incr_stream()
    from fastapi.responses import StreamingResponse
    
    async def generate():
        try:
            res_stream = agent_instance.execute_stream(request.message)
            
            for chunk in res_stream:
                # 以SSE格式发送数据
                yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"
            
            # 发送结束标记
            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
        
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )


@app.post("/api/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "agent-service"}


@app.post("/api/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    上传知识库文件接口
    :param file: 上传的文件（支持txt、pdf）
    :return: 上传结果
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        # 检查文件类型
        allowed_extensions = [".txt", ".pdf"]
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件类型，仅支持: {', '.join(allowed_extensions)}"
            )
        
        # 确保文件名安全（移除特殊字符）
        safe_filename = "".join(c for c in file.filename if c.isalnum() or c in ('.', '-', '_'))
        
        # 保存文件
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # 异步读取文件内容
        content = await file.read()
        
        # 保存文件到磁盘
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        logger.info(f"[文件上传]文件已保存: {file_path}")
        
        # 复制文件到data目录，以便向量库加载
        import shutil
        data_dir = os.path.join(project_root, "data")
        os.makedirs(data_dir, exist_ok=True)
        data_file_path = os.path.join(data_dir, safe_filename)
        shutil.copy2(file_path, data_file_path)
        
        logger.info(f"[文件上传]文件已复制到data目录: {data_file_path}")
        
        # 加载到向量库
        t_before_load = time.time()
        logger.info(f"[文件上传]开始加载文件到知识库: {safe_filename}")
        vector_store_service.load_documents()
        t_after_load = time.time()
        logger.info(
            f"[增量延迟] 文件={safe_filename} | "
            f"load_documents耗时={t_after_load - t_before_load:.2f}s"
        )

        # 知识库更新后,清除RAG缓存和Agent回复缓存
        clear_all_llm_cache()
        logger.info(f"[文件上传] 已清除RAG和Agent回复缓存")
        
        metrics.incr_upload()
        return FileUploadResponse(
            filename=safe_filename,
            message=f"文件 {safe_filename} 上传并加载到知识库成功",
            success=True
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[文件上传]文件上传失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"文件上传失败: {str(e)}"
        )


@app.post("/api/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: str = "default"):
    """
    获取对话历史接口
    :param session_id: 会话ID
    :return: 对话历史
    """
    try:
        if not redis_available:
            return ChatHistoryResponse(
                session_id=session_id,
                messages=[],
                success=True
            )
        history_key = chat_history_key(session_id)
        raw_messages = redis_client.lrange(history_key, 0, -1)
        messages = [json.loads(msg) for msg in raw_messages]
        return ChatHistoryResponse(
            session_id=session_id,
            messages=[ChatHistory(**msg) for msg in messages],
            success=True
        )
    except Exception as e:
        logger.error(f"[获取历史]获取对话历史失败: {str(e)}")
        return ChatHistoryResponse(
            session_id=session_id,
            messages=[],
            success=False
        )


@app.delete("/api/chat/history", response_model=ChatHistoryResponse)
async def clear_chat_history(session_id: str = "default"):
    """
    清空对话历史接口
    :param session_id: 会话ID
    :return: 清空后的结果
    """
    try:
        if redis_available:
            history_key = chat_history_key(session_id)
            redis_client.delete(history_key)
        
        return ChatHistoryResponse(
            session_id=session_id,
            messages=[],
            success=True
        )
    except Exception as e:
        logger.error(f"[清空历史]清空对话历史失败: {str(e)}")
        return ChatHistoryResponse(
            session_id=session_id,
            messages=[],
            success=False
        )


@app.get("/api/metrics")
async def get_metrics():
    """获取运行统计数据"""
    return metrics.get_summary()


@app.delete("/api/metrics")
async def reset_metrics():
    """重置运行统计数据"""
    metrics.reset()
    return {"message": "统计数据已重置", "success": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)