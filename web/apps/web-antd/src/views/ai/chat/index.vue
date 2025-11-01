<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue';

import { Page } from '@vben/common-ui';

import {
  Button,
  Col,
  Input,
  InputSearch,
  List,
  ListItem,
  Row,
  Select,
} from 'ant-design-vue';
import {
  createConversation,
  fetchAIStream,
  getConversations,
  getMessages,
} from '#/api/ai/chat';
import {AiChatConversationModel} from "#/models/ai/chat_conversation";
import {AiChatMessageModel} from "#/models/ai/chat_message";

const aiChatConversation = new AiChatConversationModel();
const aiChatMessageModel = new AiChatMessageModel();
interface Message {
  id: number;
  type: 'assistant' | 'user';
  content: string;
}

interface ChatItem {
  id: number;
  title: string;
  lastMessage: string;
}

// 历史对话
const chatList = ref<ChatItem[]>([]);

// 聊天消息
const messages = ref<Message[]>([]);

// 模型列表
const platformOptions = [
  { label: 'deepseek', value: 'deepseek' },
  { label: '通义千问', value: 'tongyi' },
];

const selectedChatId = ref<null | number>(chatList.value[0]?.id ?? null);
const selectedPlatform = ref(platformOptions[0]?.value);
const search = ref('');
const input = ref('');
const messagesRef = ref<HTMLElement | null>(null);
const currentAiMessage = ref<Message | null>(null);
const isAiTyping = ref(false);

const filteredChats = computed(() => {
  if (!search.value) return chatList.value;
  return chatList.value.filter((chat) => chat.title.includes(search.value));
});

async function selectChat(id: number) {
  selectedChatId.value = id;
  const data = await aiChatMessageModel.list({
    conversation_id: id,
  });
  console.log('history', data);
  messages.value = data;
  nextTick(scrollToBottom);
}

async function handleNewChat() {
  // 调用后端新建对话
  // const { data } = await createConversation(selectedPlatform.value!);
  const data = await aiChatConversation.create({
    platform: selectedPlatform.value!,
    title: '新对话',
  });
  // 刷新对话列表
  await fetchConversations();
  // 选中新建的对话
  selectedChatId.value = data;
  messages.value = [];
  nextTick(scrollToBottom);
}

async function handleSend() {
  const msg: Message = {
    id: null,
    type: 'user',
    content: input.value,
  };
  messages.value.push(msg);

  // 预留AI消息
  const aiMsgObj: Message = {
    id: null,
    type: 'assistant',
    content: '',
  };
  messages.value.push(aiMsgObj);
  const aiMsgIndex = messages.value.length - 1; // 记录AI消息的索引

  isAiTyping.value = true;

  const stream = await fetchAIStream({
    content: input.value,
    platform: selectedPlatform.value,
    conversation_id: selectedChatId.value, // 新增
  });
  if (chatList.value.length > 0) {
    chatList.value[0]!.title = input.value.slice(0, 10);
  }
  // 立刻清空输入框
  input.value = '';
  for await (const chunk of stream) {
    for (const char of chunk) {
      messages.value[aiMsgIndex]!.content += char;
      // 用 splice 替换，确保响应式
      messages.value.splice(aiMsgIndex, 1, { ...messages.value[aiMsgIndex]! });
      await nextTick();
      scrollToBottom();
      await new Promise((resolve) => setTimeout(resolve, 15));
    }
  }
  isAiTyping.value = false;
  nextTick(scrollToBottom);
}

function scrollToBottom() {
  if (messagesRef.value && messagesRef.value.scrollHeight !== undefined) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight;
  }
}

// 获取历史对话
async function fetchConversations() {
  // const { data } = await getConversations();
  const data = await aiChatConversation.list();
  console.log('history', data);
  chatList.value = data.map((item: any) => ({
    id: item.id,
    title: item.title,
    lastMessage: item.last_message || '',
  }));
  // 默认选中第一个对话
  if (chatList.value.length > 0) {
    selectedChatId.value = chatList.value[0].id;
    await selectChat(selectedChatId.value);
  }
}

onMounted(() => {
  fetchConversations();
});
</script>

<template>
  <Page auto-content-height>
    <Row style="height: 100%">
      <!-- 左侧历史对话 -->
      <Col :span="5" class="chat-sider">
        <div class="sider-header">
          <Button type="primary" @click="handleNewChat">新建对话</Button>
          <Input
            v-model:value="search"
            placeholder="搜索历史对话"
            allow-clear
            style="margin: 12px 0 8px 0"
          />
        </div>
        <div class="chat-list">
          <List style="flex: 1; overflow-y: auto; padding-bottom: 12px">
            <template #default>
              <ListItem
                v-for="item in filteredChats"
                :key="item.id"
                class="chat-list-item"
                :class="[{ selected: item.id === selectedChatId }]"
                @click="selectChat(item.id)"
              >
                <div class="chat-item-avatar">
                  <!-- 可用头像或首字母 -->
                  <span class="avatar-text">{{ item.title.slice(0, 1) }}</span>
                </div>
                <div class="chat-item-content">
                  <div class="chat-item-title-row">
                    <span class="chat-title" :title="item.title">{{
                      item.title
                    }}</span>
                    <!-- 未读角标（如有未读可加） -->
                    <!-- <span class="unread-dot"></span> -->
                  </div>
                  <div class="chat-desc">{{ item.lastMessage }}</div>
                </div>
              </ListItem>
            </template>
          </List>
        </div>
      </Col>
      <!-- 右侧聊天区 -->
      <Col :span="18" class="chat-content">
        <div class="content-header">
          <div class="model-select-wrap">
            <Select
              v-model:value="selectedPlatform"
              style="width: 220px"
              :options="platformOptions"
              placeholder="选择平台"
            />
          </div>
        </div>
        <div class="chat-messages" style="height: 100%" ref="messagesRef">
          <div
            v-for="msg in messages"
            :key="msg.id"
            class="chat-message"
            :class="[msg.type]"
          >
            <div class="bubble" :class="[msg.type]">
              <span class="role">{{ msg.type === 'user' ? '我' : 'AI' }}</span>
              <span class="bubble-content">
                {{ msg.content }}
                <span
                  v-if="
                    msg.type === 'assistant' &&
                    isAiTyping &&
                    msg === currentAiMessage
                  "
                  class="typing-cursor"
                ></span>
              </span>
            </div>
          </div>
        </div>
        <div class="chat-input-wrap">
          <InputSearch
            v-model:value="input"
            enter-button="发送"
            @search="handleSend"
            placeholder="请输入内容..."
          />
        </div>
      </Col>
    </Row>
  </Page>
</template>

<style scoped lang="css">
.chat-sider {
  background: #fafbfc;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #eee;
  padding: 16px 8px 8px 8px;
}
.sider-header {
  margin-bottom: 8px;
}
.chat-list-item {
  border-radius: 6px;
  margin-bottom: 4px;
  transition:
    box-shadow 0.2s,
    background 0.2s;
  cursor: pointer;
}
.chat-list-item.selected {
  background: #e6f7ff;
  box-shadow: 0 2px 8px #1677ff22;
  border: 1.5px solid #1677ff;
}
.chat-list-item:hover {
  background: #f0f5ff;
  box-shadow: 0 2px 8px #1677ff11;
}
.chat-title {
  font-weight: 500;
  font-size: 15px;
  max-width: 140px;
  display: inline-block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.chat-desc {
  color: #888;
  font-size: 12px;
  max-width: 140px;
  display: inline-block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.chat-content {
  display: flex;
  height: 100%;
  flex-direction: column;
  padding: 16px 24px 8px 24px;
  background: #f6f8fa;
}
.content-header {
  margin-bottom: 12px;
  display: flex;
  justify-content: flex-end;
}
.model-select-wrap {
  width: 100%;
  display: flex;
  justify-content: flex-end;
}
.chat-messages {
  flex: 1 1 auto;
  overflow-y: auto;
  background: #fff;
  border-radius: 8px;
  padding: 24px 16px 80px 16px;
  margin-bottom: 0;
  /* min-height: 300px; */
  box-shadow: 0 2px 8px #0001;
  transition: box-shadow 0.2s;
  scrollbar-width: thin;
  scrollbar-color: #d6dee1 #f6f8fa;
}
.chat-messages::-webkit-scrollbar {
  width: 6px;
}
.chat-messages::-webkit-scrollbar-thumb {
  background: #d6dee1;
  border-radius: 4px;
}
.chat-messages::-webkit-scrollbar-track {
  background: #f6f8fa;
}
.chat-message {
  display: flex;
  margin-bottom: 16px;
}
.chat-message.user {
  justify-content: flex-end;
}
.chat-message.ai {
  justify-content: flex-start;
}
.bubble {
  max-width: 70%;
  padding: 10px 16px;
  border-radius: 18px;
  font-size: 15px;
  line-height: 1.7;
  box-shadow: 0 1px 4px #0001;
  display: flex;
  align-items: center;
  word-break: break-all;
}
.bubble.user {
  background: linear-gradient(90deg, #1677ff 0%, #69b1ff 100%);
  color: #fff;
  border-bottom-right-radius: 4px;
}
.bubble.ai {
  background: #f0f5ff;
  color: #333;
  border-bottom-left-radius: 4px;
}
.role {
  font-weight: bold;
  margin-right: 8px;
  font-size: 13px;
  opacity: 0.7;
}
.bubble-content {
  flex: 1;
}
.chat-input-wrap {
  position: absolute;
  left: 24%;
  right: 24px;
  bottom: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px #0001;
  padding: 12px 16px 8px 16px;
  z-index: 10;
}
@media (max-width: 1200px) {
  .chat-input-wrap {
    left: 6%;
    right: 6px;
  }
  .chat-content {
    padding: 8px 4px 8px 4px;
  }
}
.typing-cursor {
  display: inline-block;
  width: 8px;
  height: 1.2em;
  background: #1677ff;
  margin-left: 2px;
  animation: blink-cursor 1s steps(1) infinite;
  vertical-align: bottom;
  border-radius: 2px;
}
@keyframes blink-cursor {
  0%,
  50% {
    opacity: 1;
  }
  51%,
  100% {
    opacity: 0;
  }
}
.chat-list-item {
  display: flex;
  align-items: center;
  border-radius: 8px;
  margin-bottom: 6px;
  padding: 8px 12px;
  cursor: pointer;
  transition:
    background 0.2s,
    box-shadow 0.2s;
}
.chat-list-item.selected {
  background: #e6f7ff;
  box-shadow: 0 2px 8px #1677ff22;
  border: 1.5px solid #1677ff;
}
.chat-list-item:hover {
  background: #f0f5ff;
  box-shadow: 0 2px 8px #1677ff11;
}
.chat-item-avatar {
  width: 36px;
  height: 36px;
  background: #1677ff22;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  font-size: 18px;
  color: #1677ff;
  font-weight: bold;
}
.avatar-text {
  user-select: none;
}
.chat-item-content {
  flex: 1;
  min-width: 0;
}
.chat-item-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.chat-title {
  font-weight: 500;
  font-size: 15px;
  max-width: 140px;
  display: inline-block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.unread-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  background: #ff4d4f;
  border-radius: 50%;
  margin-left: 8px;
}
.chat-desc {
  color: #888;
  font-size: 12px;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-top: 2px;
}
.chat-sider {
  background: #fafbfc;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #eee;
  padding: 16px 8px 8px 8px;
  height: 100%; /* 关键：让侧边栏高度100% */
  min-width: 220px;
}

.sider-header {
  margin-bottom: 8px;
}

.chat-list {
  flex: 1;
  overflow-y: auto; /* 只在对话列表区滚动 */
  min-height: 0; /* 关键：flex子项内滚动时必须加 */
  max-height: calc(100vh - 120px); /* 可根据实际header/footer高度调整 */
}
</style>
