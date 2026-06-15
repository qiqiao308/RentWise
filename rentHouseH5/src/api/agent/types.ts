export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp?: number;
}

export interface ChatResponse {
  response: string;
  success: boolean;
}

export interface FileUploadResponse {
  filename: string;
  message: string;
  success: boolean;
}
