package com.atguigu.lease.web.app.service.impl;

import com.atguigu.lease.web.app.service.AgentService;
import com.atguigu.lease.web.app.vo.agent.ChatRequest;
import com.atguigu.lease.web.app.vo.agent.ChatResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Slf4j
@Service
public class AgentServiceImpl implements AgentService {

    @Value("${agent.service.url:http://localhost:8000}")
    private String agentServiceUrl;

    private final RestTemplate restTemplate = new RestTemplate();

    @Override
    public ChatResponse chat(ChatRequest request) {
        try {
            String url = agentServiceUrl + "/api/chat";
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<ChatRequest> entity = new HttpEntity<>(request, headers);
            
            ResponseEntity<ChatResponse> response = restTemplate.postForEntity(url, entity, ChatResponse.class);
            
            return response.getBody() != null ? response.getBody() : 
                   new ChatResponse("抱歉,服务暂时不可用", false);
            
        } catch (Exception e) {
            log.error("调用智能客服服务失败", e);
            return new ChatResponse("抱歉,处理您的问题时出现了错误,请稍后重试", false);
        }
    }
}
