import { fetchWithAuth } from '#/utils/fetch-with-auth';

export async function getConversations() {
  const res = await fetchWithAuth('chat/conversations');
  return await res.json();
}

export async function createConversation(platform: string) {
  const response = await fetchWithAuth('chat/conversations', {
    method: 'POST',
    body: JSON.stringify({ platform }),
  });
  if (!response.ok) {
    throw new Error('创建对话失败');
  }
  return await response.json();
}

export async function getMessages(conversationId: number) {
  const res = await fetchWithAuth(
    `chat/messages?conversation_id=${conversationId}`,
  );
  return await res.json();
}

// 你原有的fetchAIStream方法保留
export interface FetchAIStreamParams {
  content: string;
  platform: string;
  conversation_id?: null | number;
}

export async function fetchAIStream({
  content,
  platform,
  conversation_id,
}: FetchAIStreamParams) {
  const res = await fetchWithAuth('ai/chat_message/stream/', {
    method: 'POST',
    body: JSON.stringify({ content, platform, conversation_id }),
  });
  if (!res.body) throw new Error('No stream body');
  const reader = res.body.getReader();
  const decoder = new TextDecoder('utf8');
  let buffer = '';
  return {
    async *[Symbol.asyncIterator]() {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split('\n\n');
        buffer = parts.pop() || '';
        for (const part of parts) {
          if (part.startsWith('data: ')) {
            yield part.replace('data: ', '');
          }
        }
      }
    },
  };
}
