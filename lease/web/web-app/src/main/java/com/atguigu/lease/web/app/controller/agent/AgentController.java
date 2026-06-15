package com.atguigu.lease.web.app.controller.agent;

import com.atguigu.lease.common.login.LoginUserHolder;
import com.atguigu.lease.common.result.Result;
import com.atguigu.lease.web.app.service.AgentService;
import com.atguigu.lease.web.app.vo.agent.ChatRequest;
import com.atguigu.lease.web.app.vo.agent.ChatResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@Tag(name = "智能客服")
@RestController
@RequestMapping("/app/agent")
public class AgentController {

    @Autowired
    private AgentService agentService;

    @PostMapping("/chat")
    @Operation(summary = "智能客服聊天")
    public Result<ChatResponse> chat(@RequestBody ChatRequest request) {
        // 从登录用户中获取userId(如果已登录)
        try {
            if (LoginUserHolder.getLoginUser() != null && LoginUserHolder.getLoginUser().getUserId() != null) {
                request.setUserId(String.valueOf(LoginUserHolder.getLoginUser().getUserId()));
            }
        } catch (Exception e) {
            // 未登录时忽略
        }
        
        ChatResponse response = agentService.chat(request);
        return Result.ok(response);
    }
}
