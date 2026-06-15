from typing import Callable
from langchain.agents import AgentState
from langchain.agents.middleware import wrap_tool_call, before_model, dynamic_prompt, ModelRequest
from langchain_core.messages import ToolMessage
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.runtime import Runtime
from langgraph.types import Command
from utils.logger_handler import logger
from utils.prompt_looader import load_system_prompts,load_report_prompts
from utils.metrics import metrics

@wrap_tool_call
def monitor_tool(
        #请求的数据封装
        request: ToolCallRequest,
        #执行的函数本身
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:     #工具执行的监控
    import time
    t_tool_start = time.perf_counter()
    logger.info(f"[tool monitor]执行工具 {request.tool_call['name']} ")
    logger.info(f"[tool monitor]执行工具 {request.tool_call['args']} ")

    try:
        result = handler( request)
        t_tool_elapsed = (time.perf_counter() - t_tool_start) * 1000
        logger.info(f"[tool monitor]工具 {request.tool_call['name']} 调用成功, 耗时 {t_tool_elapsed:.2f}ms ")
        metrics.incr_tool_call(request.tool_call["name"], t_tool_elapsed)

        if request.tool_call["name"] == "fill_context_for_report":
            request.runtime.context["report"] = True
            metrics.incr_report()
        return result
    except Exception as e:
        logger.error(f"工具 {request.tool_call['name']} 调用失败 ")
        raise e


@before_model
def log_beefore_mode(
        state: AgentState,      #整个Agent智能体中的状态记录
        runtime: Runtime,       #记录了整个执行过程中上下文信息
):         #模型执行前的日志
    logger.info(f"[log_beefore_mode]即将调用模型 {len(state['messages'])}条信息 ")
    logger.debug(f"[log_beefore_mode] {type(state['messages'][-1]).__name__} |{state['messages'][-1].content.strip()})")
    metrics.incr_middleware("log_beefore_mode")
    return None


@dynamic_prompt     #每一次在生成提示词之前,调用这个函数
def report_prompt_switch(request: ModelRequest):     #动态切换提示词
    is_report = request.runtime.context.get("report", False)
    metrics.incr_middleware("report_prompt_switch")
    if is_report:           #是报告生成场景,返回报告提示词内容
        return load_report_prompts()

    return load_system_prompts()