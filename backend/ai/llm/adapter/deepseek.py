from langchain_deepseek import ChatDeepSeek

from llm.base import MultiModalAICapability


class DeepSeekAdapter(MultiModalAICapability):
    def __init__(self, api_key, model, **kwargs):

        self.llm = ChatDeepSeek(api_key=api_key, model=model, streaming=True)

    async def chat(self, messages, **kwargs):
        # 兼容 DeepSeek 的调用方式
        return await self.llm.ainvoke(messages)

    async def stream_chat(self, messages, **kwargs):
        async for chunk in self.llm.astream(messages):
            yield chunk