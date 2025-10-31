<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';

import { Page } from '@vben/common-ui';

import {
  Button,
  Card,
  Col,
  Form,
  Input,
  message,
  Pagination,
  Row,
  Select,
  Spin,
} from 'ant-design-vue';

import { DrawingModel } from '#/models/ai/drawing';
// DrawingModel
// 定义图片对象类型
const operator = new DrawingModel();
interface DrawingImage {
  id: number;
  status: string;
  pic_url?: string;
  // 其他属性
}

// 表单选项
const platforms = [
  { label: '通义千问', value: 'tongyi' },
  // { label: 'DeepSeek', value: 'deepseek' },
  // { label: 'OpenAI', value: 'openai' },
  // { label: 'Google GenAI', value: 'google-genai' },
];

const models: Record<string, { label: string; value: string }[]> = {
  tongyi: [{ label: 'wanx_v1', value: 'wanx_v1' }],
  // 其他平台...
};

const sizes = [
  { label: '1024*1024', value: '1024*1024' },
  { label: '720*1280', value: '720*1280' },
  { label: '768*1152', value: '768*1152' },
  { label: '1280*720', value: '1280*720' },
];
const styles = [
  { label: '默认（由模型随机输出风格）', value: 'auto' },
  { label: '摄影', value: 'photography' },
  { label: '人像写真', value: 'portrait' },
  { label: '3D卡通', value: '3d cartoon' },
  { label: '动画', value: 'anime' },
  { label: '油画', value: 'oil painting' },
  { label: '水彩', value: 'watercolor' },
  { label: '素描', value: 'sketch' },
  { label: '中国画', value: 'chinese painting' },
  { label: '扁平插画', value: 'flat illustration' },
];

// 表单数据
const form = reactive({
  prompt:
    '近景镜头，18岁的中国女孩，古代服饰，圆脸，正面看着镜头，民族优雅的服装，商业摄影，室外，电影级光照，半身特写，精致的淡妆，锐利的边缘。',
  platform: 'tongyi',
  model: 'wanx-v1',
  size: '1024*1024',
  style: 'watercolor',
});

// 图片数据与分页
const images = ref<DrawingImage[]>([]);
const loading = ref(false);
const page = ref(1);
const pageSize = ref(9);
const total = ref(0);

// 平台切换时自动切换模型
const onPlatformChange = (value: number | string) => {
  form.model = models[value as string]?.[0]?.value ?? '';
};

// 提交表单，调用AI画图API
async function handleDraw() {
  loading.value = true;
  try {
    // 这里调用你的AI画图API，返回图片url数组
    await operator.create(form);
    page.value = 1;
    await fetchDrawingList(page.value, pageSize.value); // 刷新第一页图片列表
    // images.value = res.data.images;
    // DEMO用假数据
    message.success('生成成功');
  } catch {
    message.error('生成失败');
  } finally {
    loading.value = false;
  }
}
let drawingTimer: NodeJS.Timeout | null = null;

// 轮询获取图片详情
const pollDrawingDetail = async (id: number) => {
  try {
    const res = await operator.retrieve(id); // 改用 await 简化代码
    if (res?.status === 'RUNNING') {
      // 保存定时器 ID，方便后续清除
      drawingTimer = setTimeout(() => pollDrawingDetail(id), 5000);
    } else if (
      res?.status === '"SUCCEEDED"' && // 当状态为 "SUCCEEDED" 时，清除定时器
      drawingTimer
    ) {
      clearTimeout(drawingTimer);
      drawingTimer = null; // 重置定时器 ID
      await fetchDrawingList();
      // 可在此处添加任务成功后的其他逻辑（如刷新页面、提示用户等）
    }
    // 可根据需要添加对其他状态的处理（如 FAILED）
  } catch (error) {
    // 处理请求失败的情况，避免轮询异常中断
    console.error('轮询失败:', error);
    if (drawingTimer) {
      clearTimeout(drawingTimer);
      drawingTimer = null;
    }
  }
};

// 获取图片分页列表
async function fetchDrawingList(pageNum = 1, pageSize = 9) {
  try {
    const res = await operator.list({
      page: pageNum,
      pageSize,
    });
    images.value = res.items;
    // images.value = res.items.map(item => item.pic_url);
    total.value = res.total;
    // 检查每个 item 的状态
    for (const item of res.items) {
      if (item.status === 'PENDING' || item.status === 'RUNNING') {
        pollDrawingDetail(item.id);
      }
    }
    return res;
  } catch {
    message.error('获取图片列表失败');
    return null;
  }
}

// 页面加载时调用获取图片列表
onMounted(() => {
  fetchDrawingList();
});
</script>

<template>
  <Page auto-content-height>
    <Row :gutter="24">
      <!-- 左侧表单 -->
      <Col :span="8">
        <Card title="AI画图" bordered>
          <Form layout="vertical" @submit.prevent="handleDraw">
            <Form.Item label="画画描述">
              <Input.TextArea
                v-model:value="form.prompt"
                :auto-size="true"
                placeholder="请输入画面描述"
              />
            </Form.Item>
            <Form.Item label="平台选择">
              <Select v-model:value="form.platform" @change="onPlatformChange">
                <Select.Option
                  v-for="item in platforms"
                  :key="item.value"
                  :value="item.value"
                >
                  {{ item.label }}
                </Select.Option>
              </Select>
            </Form.Item>
            <Form.Item label="模型选择">
              <Select v-model:value="form.model">
                <Select.Option
                  v-for="item in models[form.platform]"
                  :key="item.value"
                  :value="item.value"
                >
                  {{ item.label }}
                </Select.Option>
              </Select>
            </Form.Item>
            <Form.Item label="图片尺寸">
              <Select v-model:value="form.size">
                <Select.Option
                  v-for="item in sizes"
                  :key="item.value"
                  :value="item.value"
                >
                  {{ item.label }}
                </Select.Option>
              </Select>
            </Form.Item>
            <Form.Item label="图像风格">
              <Select v-model:value="form.style">
                <Select.Option
                  v-for="item in styles"
                  :key="item.value"
                  :value="item.value"
                >
                  {{ item.label }}
                </Select.Option>
              </Select>
            </Form.Item>
            <Form.Item>
              <Button type="primary" html-type="submit" :loading="loading">
                生成图片
              </Button>
            </Form.Item>
          </Form>
        </Card>
      </Col>
      <!-- 右侧图片展示 -->
      <Col :span="16">
        <Card title="生成结果" bordered>
          <Row :gutter="16">
            <Col
              v-for="(img, idx) in images"
              :key="idx"
              :span="8"
              style="margin-bottom: 16px"
            >
              <Card hoverable>
                <template #cover>
                  <div
                    v-if="img.status === 'PENDING' || img.status === 'RUNNING'"
                    style="
                      width: 100%;
                      height: 180px;
                      display: flex;
                      align-items: center;
                      justify-content: center;
                    "
                  >
                    <Spin size="large" />
                  </div>
                  <img
                    v-else
                    :src="img.pic_url"
                    style="width: 100%; height: 180px; object-fit: cover"
                  />
                </template>
              </Card>
            </Col>
          </Row>
          <Pagination
            v-model:current="page"
            :total="total"
            :page-size="pageSize"
            style="margin-top: 16px; text-align: right"
            @change="
              (p, ps) => {
                page = p;
                pageSize = ps;
                fetchDrawingList(p, ps);
              }
            "
          />
        </Card>
      </Col>
    </Row>
  </Page>
</template>

<style scoped>
/* 可根据需要自定义样式 */
</style>
