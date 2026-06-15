import redis
import yaml
from typing import Optional
from utils.path_tool import get_abs_path
from utils.logger_handler import logger


def _load_redis_config(config_path: str = get_abs_path("config/redis.yml"), encoding: str = "utf-8") -> dict:
    """加载Redis配置文件"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


redis_conf = _load_redis_config()

# 全局状态标记: Redis是否可用
redis_available = False
# 全局Redis客户端实例(连接失败时为 None)
redis_client: Optional[redis.Redis] = None

try:
    _pool = redis.ConnectionPool(
        host=redis_conf.get("host", "localhost"),
        port=redis_conf.get("port", 6379),
        db=redis_conf.get("db", 0),
        decode_responses=redis_conf.get("decode_responses", True),
    )
    redis_client = redis.Redis(connection_pool=_pool)
    redis_client.ping()
    redis_available = True
    logger.info("[Redis] 连接成功")
except redis.ConnectionError as e:
    logger.warning(f"[Redis] 连接失败: {e} → 降级运行(缓存功能禁用)")
except Exception as e:
    logger.warning(f"[Redis] 初始化异常: {e} → 降级运行(缓存功能禁用)")


# ============ 缓存Key生成工具 ============

import hashlib


def rag_cache_key(query: str) -> str:
    """生成RAG摘要结果的缓存key"""
    query_hash = hashlib.md5(query.strip().encode("utf-8")).hexdigest()
    return f"rag:summarize:{query_hash}"


def agent_reply_cache_key(message: str) -> str:
    """生成Agent回复的缓存key"""
    msg_hash = hashlib.md5(message.strip().lower().encode("utf-8")).hexdigest()
    return f"agent:reply:{msg_hash}"


def chat_history_key(session_id: str) -> str:
    """生成对话历史的缓存key"""
    return f"chat:history:{session_id}"


# ============ 缓存清除工具 ============

def clear_rag_cache():
    """清除所有RAG摘要缓存"""
    if not redis_available:
        return
    try:
        keys = list(redis_client.scan_iter("rag:summarize:*"))
        if keys:
            redis_client.delete(*keys)
        logger.info(f"[Redis缓存] 已清除RAG缓存 {len(keys)} 条")
    except Exception as e:
        logger.warning(f"[Redis缓存] 清除RAG缓存失败: {e}")


def clear_agent_reply_cache():
    """清除所有Agent回复缓存"""
    if not redis_available:
        return
    try:
        keys = list(redis_client.scan_iter("agent:reply:*"))
        if keys:
            redis_client.delete(*keys)
        logger.info(f"[Redis缓存] 已清除Agent回复缓存 {len(keys)} 条")
    except Exception as e:
        logger.warning(f"[Redis缓存] 清除Agent回复缓存失败: {e}")


def clear_all_llm_cache():
    """清除所有LLM相关缓存（知识库更新时调用）"""
    clear_rag_cache()
    clear_agent_reply_cache()


if __name__ == '__main__':
    print("Redis连接测试:", redis_client.ping())
    print("Redis配置:", redis_conf)