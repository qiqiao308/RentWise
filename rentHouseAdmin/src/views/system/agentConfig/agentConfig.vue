<template>
  <div class="agent-config-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>智能客服配置</span>
        </div>
      </template>

      <el-form :model="configForm" label-width="150px" style="max-width: 600px">
        <el-form-item label="Agent服务地址">
          <el-input v-model="configForm.agentServiceUrl" placeholder="http://localhost:8000" />
          <div class="form-tip">Python Agent服务的URL地址</div>
        </el-form-item>

        <el-form-item label="服务状态">
          <el-tag :type="serviceStatus === 'online' ? 'success' : 'danger'">
            {{ serviceStatus === 'online' ? '在线' : '离线' }}
          </el-tag>
          <el-button type="primary" link @click="checkServiceStatus" style="margin-left: 10px">
            检测状态
          </el-button>
        </el-form-item>

        <el-form-item label="知识库文件">
          <el-upload
            class="upload-demo"
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            multiple
          >
            <el-button type="primary">上传知识库文件</el-button>
            <template #tip>
              <div class="el-upload__tip">支持 .txt, .pdf 格式文件</div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveConfig">保存配置</el-button>
          <el-button @click="resetConfig">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="box-card" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>聊天记录统计</span>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="今日对话数">
          {{ stats.todayConversations }}
        </el-descriptions-item>
        <el-descriptions-item label="总对话数">
          {{ stats.totalConversations }}
        </el-descriptions-item>
        <el-descriptions-item label="平均响应时间">
          {{ stats.avgResponseTime }}ms
        </el-descriptions-item>
        <el-descriptions-item label="用户满意度">
          {{ stats.satisfactionRate }}%
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage } from "element-plus";

const configForm = reactive({
  agentServiceUrl: "http://localhost:8000"
});

const serviceStatus = ref("offline");

const stats = reactive({
  todayConversations: 0,
  totalConversations: 0,
  avgResponseTime: 0,
  satisfactionRate: 0
});

// 检测服务状态
const checkServiceStatus = async () => {
  try {
    // TODO: 调用后端API检测服务状态
    const response = await fetch(`${configForm.agentServiceUrl}/api/health`);
    if (response.ok) {
      serviceStatus.value = "online";
      ElMessage.success("服务在线");
    } else {
      serviceStatus.value = "offline";
      ElMessage.error("服务离线");
    }
  } catch (error) {
    serviceStatus.value = "offline";
    ElMessage.error("无法连接到服务");
  }
};

// 处理文件上传
const handleFileChange = (file: any) => {
  console.log("文件:", file);
  ElMessage.info(`已选择文件: ${file.name}`);
};

// 保存配置
const saveConfig = () => {
  // TODO: 调用后端API保存配置
  ElMessage.success("配置保存成功");
};

// 重置配置
const resetConfig = () => {
  configForm.agentServiceUrl = "http://localhost:8000";
  ElMessage.info("已重置配置");
};

onMounted(() => {
  checkServiceStatus();
  // TODO: 加载统计数据
});
</script>

<style scoped lang="scss">
.agent-config-container {
  padding: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: bold;
  }

  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 5px;
  }
}
</style>
