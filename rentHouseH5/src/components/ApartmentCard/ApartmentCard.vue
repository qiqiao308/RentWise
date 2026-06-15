<template>
  <van-card
    class="rounded-xl shadow"
    :title="`${data.name}`"
    :desc="`${data.provinceName} ${data.cityName} ${data.districtName}`"
    @click="goApartmentDetail"
  >
    <template #price>
      <!--      价格-->
      <span class="text-red-500 text-[14px]">￥</span>
      <span class="text-red-500 text-[16px]">{{ data.minRent }}/月起</span>
    </template>
    <!--    thumb-->
    <template #thumb>
      <van-image
        class="w-full h-full object-cover"
        :src="convertedGraphVoList?.[0]?.url || '失败'"
      >
        <template v-slot:error>加载失败</template>
        <template v-slot:loading>
          <van-loading type="spinner" size="20" />
        </template>
      </van-image>
    </template>
    <template #tags>
      <van-tag
        class="last:mr-0 mr-[5px]"
        plain
        v-for="item in data.labelInfoList"
        :key="item.id"
        type="primary"
        >{{ item.name }}
      </van-tag>
    </template>
  </van-card>
</template>

<script setup lang="ts">
import type { ApartmentInterface } from "@/api/search/types";
import type { PropType } from "vue";
import { useRouter } from "vue-router";
import { computed } from "vue";
const router = useRouter();

const props = defineProps({
  // 房间的信息数据
  data: {
    type: Object as PropType<ApartmentInterface>,
    default: () => ({}),
    readOnly: true
  }
});

// 转换后的图片列表
const convertedGraphVoList = computed(() => {
  if (!props.data.graphVoList) return [];
  return props.data.graphVoList.map(item => {
    if (item.url && item.url.startsWith('http')) {
      const urlObj = new URL(item.url);
      const path = urlObj.pathname;
      return { ...item, url: '/minio' + path };
    }
    return item;
  });
});

// 跳转到公寓的详情页面
const goApartmentDetail = () => {
  router.push({ path: "/apartmentDetail", query: { id: props.data.id } });
};
</script>

<style scoped></style>
