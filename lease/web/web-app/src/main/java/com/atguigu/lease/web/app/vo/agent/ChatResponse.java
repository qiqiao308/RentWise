package com.atguigu.lease.web.app.vo.agent;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "智能客服聊天响应")
public class ChatResponse {
    
    @Schema(description = "AI回复内容")
    private String response;
    
    @Schema(description = "是否成功")
    private Boolean success;
}
