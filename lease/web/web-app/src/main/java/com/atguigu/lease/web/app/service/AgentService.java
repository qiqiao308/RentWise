package com.atguigu.lease.web.app.service;

import com.atguigu.lease.web.app.vo.agent.ChatRequest;
import com.atguigu.lease.web.app.vo.agent.ChatResponse;

public interface AgentService {
    
    /**
     * 智能客服聊天
     * @param request 聊天请求
     * @return 聊天响应
     */
    ChatResponse chat(ChatRequest request);
}
