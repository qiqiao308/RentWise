import request from "@/utils/http";

// 智能客服聊天接口
export function chatWithAgent(data: { message: string; userId?: string; sessionId?: string }) {
  return request.post(
    "/api/chat",
    data
  );
}

// 上传知识库文件
export function uploadKnowledgeFile(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return request.post("/api/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
}

// 清空对话历史
export function clearChatHistory(sessionId?: string) {
  return request.delete("/api/chat/history", {
    params: { session_id: sessionId || "default" }
  });
}

// 获取对话历史
export function getChatHistory(sessionId?: string) {
  return request.post("/api/chat/history", null, {
    params: { session_id: sessionId || "default" }
  });
}
