import time
import threading
from collections import defaultdict
from contextlib import contextmanager
from utils.logger_handler import logger as metrics_logger


class MetricsCollector:
    def __init__(self):
        self._lock = threading.Lock()
        self._reset()

        self._redis_available = False
        try:
            from utils.redis_handler import redis_client, redis_available
            if redis_available and redis_client is not None:
                self._redis = redis_client
                self._redis_available = True
                metrics_logger.info("[Metrics] Redis 连接成功, 统计数据持久化到 Redis")
            else:
                metrics_logger.warning("[Metrics] Redis 不可用, 统计数据仅保存在内存中")
        except Exception:
            metrics_logger.warning("[Metrics] Redis 不可用, 统计数据仅保存在内存中")

    def _reset(self):
        self._api_requests = 0
        self._api_success = 0
        self._api_failure = 0
        self._api_total_time_ms = 0.0
        self._api_min_time_ms = float('inf')
        self._api_max_time_ms = 0.0

        self._agent_cache_hit = 0
        self._agent_cache_miss = 0
        self._rag_cache_hit = 0
        self._rag_cache_miss = 0

        self._rag_total_retrieval_ms = 0.0
        self._rag_retrieval_count = 0
        self._rag_total_docs = 0

        self._tool_calls = defaultdict(int)
        self._tool_total_time_ms = 0.0
        self._tool_call_count = 0

        self._report_generated = 0
        self._stream_count = 0
        self._upload_count = 0
        self._middleware_calls = defaultdict(int)

    def _redis_incr(self, key, amount=1):
        if self._redis_available:
            try:
                self._redis.incrby(key, amount)
            except Exception:
                pass

    def incr_api(self, success: bool, elapsed_ms: float):
        with self._lock:
            self._api_requests += 1
            if success:
                self._api_success += 1
            else:
                self._api_failure += 1
            self._api_total_time_ms += elapsed_ms
            if elapsed_ms < self._api_min_time_ms:
                self._api_min_time_ms = elapsed_ms
            if elapsed_ms > self._api_max_time_ms:
                self._api_max_time_ms = elapsed_ms
        self._redis_incr("metrics:api:requests")
        self._redis_incr("metrics:api:success" if success else "metrics:api:failure")

    def incr_agent_cache_hit(self):
        with self._lock:
            self._agent_cache_hit += 1
        self._redis_incr("metrics:agent:cache_hit")

    def incr_agent_cache_miss(self):
        with self._lock:
            self._agent_cache_miss += 1
        self._redis_incr("metrics:agent:cache_miss")

    def incr_rag_cache_hit(self):
        with self._lock:
            self._rag_cache_hit += 1
        self._redis_incr("metrics:rag:cache_hit")

    def incr_rag_cache_miss(self):
        with self._lock:
            self._rag_cache_miss += 1
        self._redis_incr("metrics:rag:cache_miss")

    def incr_rag_retrieval(self, elapsed_ms: float, doc_count: int):
        with self._lock:
            self._rag_retrieval_count += 1
            self._rag_total_retrieval_ms += elapsed_ms
            self._rag_total_docs += doc_count
        self._redis_incr("metrics:rag:retrievals")

    def incr_tool_call(self, tool_name: str, elapsed_ms: float):
        with self._lock:
            self._tool_calls[tool_name] += 1
            self._tool_call_count += 1
            self._tool_total_time_ms += elapsed_ms
        self._redis_incr(f"metrics:tool:{tool_name}")
        self._redis_incr("metrics:tool:total")

    def incr_report(self):
        with self._lock:
            self._report_generated += 1
        self._redis_incr("metrics:report:generated")

    def incr_stream(self):
        with self._lock:
            self._stream_count += 1
        self._redis_incr("metrics:api:stream")

    def incr_upload(self):
        with self._lock:
            self._upload_count += 1
        self._redis_incr("metrics:api:upload")

    def incr_middleware(self, name: str):
        with self._lock:
            self._middleware_calls[name] += 1
        self._redis_incr(f"metrics:middleware:{name}")

    @contextmanager
    def track_time(self, metric_key: str | None = None):
        t0 = time.perf_counter()
        try:
            yield
        finally:
            elapsed = (time.perf_counter() - t0) * 1000
            if metric_key:
                self._redis_incr(f"metrics:time:{metric_key}", int(elapsed))

    def get_summary(self) -> dict:
        with self._lock:
            api_count = self._api_requests
            api_avg = self._api_total_time_ms / api_count if api_count > 0 else 0
            api_min = self._api_min_time_ms if self._api_min_time_ms != float('inf') else 0
            api_max = self._api_max_time_ms

            agent_total = self._agent_cache_hit + self._agent_cache_miss
            agent_hit_rate = self._agent_cache_hit / agent_total * 100 if agent_total > 0 else 0

            rag_total = self._rag_cache_hit + self._rag_cache_miss
            rag_hit_rate = self._rag_cache_hit / rag_total * 100 if rag_total > 0 else 0

            rag_avg_retrieval = self._rag_total_retrieval_ms / self._rag_retrieval_count if self._rag_retrieval_count > 0 else 0
            rag_avg_docs = self._rag_total_docs / self._rag_retrieval_count if self._rag_retrieval_count > 0 else 0

            tool_avg_time = self._tool_total_time_ms / self._tool_call_count if self._tool_call_count > 0 else 0

            return {
                "api": {
                    "total_requests": api_count,
                    "success": self._api_success,
                    "failure": self._api_failure,
                    "success_rate": f"{self._api_success / api_count * 100:.1f}%" if api_count > 0 else "N/A",
                    "avg_response_ms": round(api_avg, 2),
                    "min_response_ms": round(api_min, 2),
                    "max_response_ms": round(api_max, 2),
                },
                "cache": {
                    "agent_cache_hit": self._agent_cache_hit,
                    "agent_cache_miss": self._agent_cache_miss,
                    "agent_hit_rate": f"{agent_hit_rate:.1f}%",
                    "rag_cache_hit": self._rag_cache_hit,
                    "rag_cache_miss": self._rag_cache_miss,
                    "rag_hit_rate": f"{rag_hit_rate:.1f}%",
                },
                "rag": {
                    "retrieval_count": self._rag_retrieval_count,
                    "avg_retrieval_ms": round(rag_avg_retrieval, 2),
                    "total_docs_retrieved": self._rag_total_docs,
                    "avg_docs_per_query": round(rag_avg_docs, 2),
                },
                "tools": {
                    "total_calls": self._tool_call_count,
                    "avg_time_ms": round(tool_avg_time, 2),
                    "per_tool": dict(self._tool_calls),
                },
                "business": {
                    "reports_generated": self._report_generated,
                    "stream_requests": self._stream_count,
                    "file_uploads": self._upload_count,
                },
                "middleware": dict(self._middleware_calls),
            }

    def print_summary(self):
        s = self.get_summary()
        lines = [
            "",
            "=" * 60,
            "  Agent 运行统计报告",
            "=" * 60,
            "",
            "[API 接口统计]",
            f"  总请求数:      {s['api']['total_requests']}",
            f"  成功 / 失败:    {s['api']['success']} / {s['api']['failure']}",
            f"  成功率:        {s['api']['success_rate']}",
            f"  平均响应:      {s['api']['avg_response_ms']} ms",
            f"  最快响应:      {s['api']['min_response_ms']} ms",
            f"  最慢响应:      {s['api']['max_response_ms']} ms",
            "",
            "[缓存命中统计]",
            f"  Agent 缓存命中: {s['cache']['agent_cache_hit']}  未命中: {s['cache']['agent_cache_miss']}  命中率: {s['cache']['agent_hit_rate']}",
            f"  RAG  缓存命中:  {s['cache']['rag_cache_hit']}  未命中: {s['cache']['rag_cache_miss']}  命中率: {s['cache']['rag_hit_rate']}",
            "",
            "[RAG 检索统计]",
            f"  检索次数:      {s['rag']['retrieval_count']}",
            f"  平均检索耗时:  {s['rag']['avg_retrieval_ms']} ms",
            f"  检索文档总数:  {s['rag']['total_docs_retrieved']}",
            f"  每次平均文档:  {s['rag']['avg_docs_per_query']}",
            "",
            "[工具调用统计]",
            f"  总调用次数:    {s['tools']['total_calls']}",
            f"  平均耗时:      {s['tools']['avg_time_ms']} ms",
        ]
        for tool, count in s['tools']['per_tool'].items():
            lines.append(f"    {tool}: {count} 次")
        lines += [
            "",
            "[业务统计]",
            f"  报告生成次数:  {s['business']['reports_generated']}",
            f"  流式请求数:    {s['business']['stream_requests']}",
            f"  文件上传次数:  {s['business']['file_uploads']}",
            "",
            "[中间件调用]",
        ]
        for mw, count in s['middleware'].items():
            lines.append(f"    {mw}: {count} 次")
        lines += [
            "",
            "=" * 60,
        ]
        for line in lines:
            metrics_logger.info(line)
        return "\n".join(lines)

    def reset(self):
        with self._lock:
            self._reset()
        if self._redis_available:
            try:
                keys = list(self._redis.scan_iter("metrics:*"))
                if keys:
                    self._redis.delete(*keys)
            except Exception:
                pass
        metrics_logger.info("[Metrics] 统计数据已重置")


metrics = MetricsCollector()