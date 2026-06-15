<template>
  <div class="chat-container">
    <!-- 顶部导航栏 -->
    <van-nav-bar
      title="智能客服"
      left-arrow
      fixed
      placeholder
      @click-left="goBack"
    />
    <!-- 聊天消息列表 -->
    <div ref="messageListRef" class="message-list">
      <!-- 欢迎消息 -->
      <div v-if="messages.length === 0" class="welcome-message">
        <van-image
          width="80"
          height="80"
          src="https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg"
          round
        />
        <div class="welcome-text">
          <h3>您好!我是租房智能助手</h3>
          <p>有什么可以帮助您的吗?</p>
        </div>
      </div>

      <!-- 清空历史按钮 -->
      <div v-if="messages.length > 0" class="clear-btn-wrapper">
        <van-button plain type="primary" size="small" @click="clearHistory">
          <van-icon name="delete-o" style="margin-right: 4px" />
          清空聊天记录
        </van-button>
      </div>

      <!-- 消息列表 -->
      <div v-for="(msg, index) in messages" :key="index" class="message-item">
        <!-- 用户消息 -->
        <div v-if="msg.role === 'user'" class="user-message">
          <div class="message-content">{{ msg.content }}</div>
          <van-image
            width="40"
            height="40"
            src="https://fastly.jsdelivr.net/npm/@vant/assets/user-avatar.png"
            round
          />
        </div>

        <!-- AI消息 -->
        <div v-else class="assistant-message">
          <van-image
            width="40"
            height="40"
            src="https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg"
            round
          />
          <div class="message-content">
            <div v-if="msg.content" class="text-content">{{ msg.content }}</div>
            <van-loading v-else size="20px" vertical>思考中...</van-loading>
          </div>
        </div>
      </div>

      <!-- 加载更多指示器 -->
      <div v-if="loading" class="loading-indicator">
        <van-loading size="24px" />
      </div>
    </div>

    <!-- 底部输入框 -->
    <div class="input-area">
      <!-- 文件上传按钮 -->
      <div class="upload-btn-wrapper">
        <van-button plain type="primary" size="small" @click="triggerFileUpload">
          <van-icon name="upload" style="margin-right: 4px" />
          上传文件
        </van-button>
        <input
          ref="fileInputRef"
          type="file"
          accept=".txt,.pdf"
          style="display: none"
          @change="handleFileUpload"
        />
      </div>

      <van-field
        v-model="inputMessage"
        type="textarea"
        placeholder="请输入您的问题..."
        :autosize="{ minHeight: 40, maxHeight: 120 }"
        :disabled="loading"
        @keydown.enter.prevent="handleEnter"
      >
        <template #button>
          <van-button
            size="small"
            type="primary"
            :loading="loading"
            :disabled="!inputMessage.trim() || loading"
            @click="sendMessage"
          >
            发送
          </van-button>
        </template>
      </van-field>
    </div>
  </div>
</template>

<script setup lang="ts" name="AgentChat">
import { ref, nextTick, onMounted } from "vue";
import { useRouter } from "vue-router";
import { showToast, showDialog } from "vant";
import { chatWithAgent, uploadKnowledgeFile, clearChatHistory } from "@/api/agent";
import type { ChatMessage } from "@/api/agent/types";

const router = useRouter();

// 返回上一页
const goBack = () => {
  router.back();
};
const messageListRef = ref<HTMLElement | null>(null);
const fileInputRef = ref<HTMLInputElement | null>(null);
const messages = ref<ChatMessage[]>([]);
const inputMessage = ref("");
const loading = ref(false);
const uploading = ref(false);

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick();
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight;
  }
};

// 发送消息
const sendMessage = async () => {
  const message = inputMessage.value.trim();
  if (!message || loading.value) return;

  // 添加用户消息
  messages.value.push({
    role: "user",
    content: message,
    timestamp: Date.now()
  });

  // 清空输入框
  inputMessage.value = "";

  // 添加AI占位消息
  const aiMessageIndex = messages.value.length;
  messages.value.push({
    role: "assistant",
    content: "",
    timestamp: Date.now()
  });

  await scrollToBottom();

  // 调用API
  loading.value = true;
  try {
    const res = await chatWithAgent({ message });
    
    if (res.success) {
      messages.value[aiMessageIndex].content = res.response;
    } else {
      messages.value[aiMessageIndex].content = res.response || "抱歉,我遇到了一些问题,请稍后重试";
      showToast({ type: 'fail', message: '回复失败' });
    }
  } catch (error: any) {
    messages.value[aiMessageIndex].content = "网络错误,请检查网络连接后重试";
    showToast({ type: 'fail', message: '网络错误' });
    console.error("聊天失败:", error);
  } finally {
    loading.value = false;
    await scrollToBottom();
  }
};

// 回车发送
const handleEnter = (e: KeyboardEvent) => {
  if (!e.shiftKey) {
    sendMessage();
  }
};

// 清空聊天记录
const clearHistory = async () => {
  try {
    await showDialog({
      title: '提示',
      message: '确定要清空聊天记录吗？',
    });
    
    // 调用后端API清空历史
    await clearChatHistory();
    messages.value = [];
    showToast({ type: 'success', message: '已清空聊天记录' });
  } catch (error) {
    // 用户取消
  }
};

// 触发文件上传
const triggerFileUpload = () => {
  fileInputRef.value?.click();
};

// 处理文件上传
const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  
  if (!file) return;
  
  // 检查文件类型
  const allowedTypes = ['.txt', '.pdf'];
  const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
  
  if (!allowedTypes.includes(fileExt)) {
    showToast({ type: 'fail', message: '仅支持上传.txt和.pdf文件' });
    return;
  }
  
  // 检查文件大小（限制10MB）
  if (file.size > 10 * 1024 * 1024) {
    showToast({ type: 'fail', message: '文件大小不能超过10MB' });
    return;
  }
  
  uploading.value = true;
  
  try {
    const res = await uploadKnowledgeFile(file);
    
    if (res.success) {
      showToast({ type: 'success', message: res.message || '文件上传成功' });
      
      // 在聊天框中显示上传成功消息
      messages.value.push({
        role: 'assistant',
        content: `✅ 文件 "${file.name}" 已成功上传到知识库`,
        timestamp: Date.now()
      });
    } else {
      showToast({ type: 'fail', message: res.message || '文件上传失败' });
    }
  } catch (error: any) {
    showToast({ type: 'fail', message: '文件上传失败，请重试' });
    console.error('文件上传失败:', error);
  } finally {
    uploading.value = false;
    // 清空文件输入框
    if (target) target.value = '';
    await scrollToBottom();
  }
};

// 页面加载时滚动到底部
onMounted(() => {
  scrollToBottom();
});
</script>

<style lang="less" scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 50px); // 减去底部Tabbar高度
  background-color: #f5f5f5;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  padding-bottom: 80px;
  padding-top: 16px; // 调整顶部间距，因为NavBar已经用了placeholder
}

.welcome-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;

  .welcome-text {
    margin-top: 16px;

    h3 {
      font-size: 18px;
      color: #323233;
      margin-bottom: 8px;
    }

    p {
      font-size: 14px;
      color: #969799;
    }
  }
}

.clear-btn-wrapper {
  display: flex;
  justify-content: center;
  margin: 16px 0;
}

.message-item {
  margin-bottom: 16px;
}

.user-message {
  display: flex;
  justify-content: flex-end;
  align-items: flex-start;
  gap: 8px;

  .message-content {
    max-width: 70%;
    padding: 12px 16px;
    background-color: #07c160;
    color: white;
    border-radius: 12px;
    font-size: 14px;
    line-height: 1.6;
    word-wrap: break-word;
  }
}

.assistant-message {
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  gap: 8px;

  .message-content {
    max-width: 70%;
    padding: 12px 16px;
    background-color: white;
    color: #323233;
    border-radius: 12px;
    font-size: 14px;
    line-height: 1.6;
    word-wrap: break-word;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);

    .text-content {
      white-space: pre-wrap;
    }
  }
}

.loading-indicator {
  display: flex;
  justify-content: center;
  padding: 16px;
}

.input-area {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: white;
  border-top: 1px solid #ebedf0;
  padding: 8px;
  z-index: 100;

  .upload-btn-wrapper {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 8px;
  }

  :deep(.van-field) {
    padding: 0;
  }

  :deep(.van-field__body) {
    display: flex;
    align-items: flex-end;
    gap: 8px;
  }

  :deep(.van-field__control) {
    flex: 1;
    min-height: 40px;
    max-height: 120px;
    padding: 8px 12px;
    background-color: #f7f8fa;
    border-radius: 8px;
  }
}
</style>
