package com.atguigu.lease.web.app.vo.agent;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Data
@Schema(description = "智能客服聊天请求")
public class ChatRequest {
    
    @Schema(description = "用户消息")
    private String message;
    
    @Schema(description = "用户ID")
    private String userId;
    
    @Schema(description = "会话ID")
    private String sessionId;
}
