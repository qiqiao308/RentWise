import time
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from rag.vector_store import VectorStoreService
from utils.prompt_looader import load_rag_prompts
from model.factory import chat_model
from utils.logger_handler import logger
from utils.redis_handler import redis_client, redis_available, redis_conf, rag_cache_key
from utils.metrics import metrics

def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("="*20)
    return prompt


class RagSummarizeService(object):
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = load_rag_prompts()
        self.prompt_template =PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self._init_chain()
        self.rag_ttl = redis_conf.get("rag_summarize_ttl", 3600)

    def _init_chain(self):
        chain = self.prompt_template | print_prompt |self.model | StrOutputParser()
        return chain

    def retriever_docs(self,query: str) -> list[Document]:
        return self.retriever.invoke(query)

    def rag_summarize(self,query: str) ->str:
        # 1. 尝试从Redis缓存获取(Redis不可用时直接跳过)
        if redis_available:
            cache_key = rag_cache_key(query)
            try:
                cached_result = redis_client.get(cache_key)
                if cached_result:
                    logger.info(f"[RAG缓存] 命中缓存: {query}")
                    metrics.incr_rag_cache_hit()
                    return cached_result
                else:
                    metrics.incr_rag_cache_miss()
            except Exception as e:
                logger.warning(f"[RAG缓存] Redis读取异常,降级走LLM: {e}")
                metrics.incr_rag_cache_miss()
        else:
            metrics.incr_rag_cache_miss()

        # 2. 缓存未命中,走正常RAG流程
        t_retrieval_start = time.perf_counter()
        contxet_docs = self.retriever_docs(query)
        t_retrieval_elapsed = (time.perf_counter() - t_retrieval_start) * 1000

        contxet =""
        counter = 0
        for doc in contxet_docs:
            counter +=1
            contxet +=f"[参考资料{counter}]:参考资料:{doc.page_content} | 参考元数据:{doc.metadata}\n"

        metrics.incr_rag_retrieval(t_retrieval_elapsed, counter)

        result = self.chain.invoke(
            {"input": query,
             "context": contxet,
             }

        )

        # 3. 将结果写入缓存(Redis不可用时跳过)
        if redis_available:
            try:
                redis_client.setex(cache_key, self.rag_ttl, result)
                logger.info(f"[RAG缓存] 结果已缓存, TTL={self.rag_ttl}s: {query}")
            except Exception as e:
                logger.warning(f"[RAG缓存] Redis写入异常: {e}")

        return result


if __name__ == '__main__':
    rag = RagSummarizeService()

    r = rag.rag_summarize("租房押金一般多少")

    print(r)