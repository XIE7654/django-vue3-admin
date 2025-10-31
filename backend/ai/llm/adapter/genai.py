# 假设有 google genai sdk
# from google_genai import GenAI
from llm.base import MultiModalAICapability


class GoogleGenAIAdapter(MultiModalAICapability):
    def __init__(self, api_key, model, **kwargs):
        self.api_key = api_key
        self.model = model
        # self.llm = GenAI(api_key=api_key, model=model)

    async def chat(self, messages, **kwargs):
        # return await self.llm.chat(messages)
        raise NotImplementedError("Google GenAI chat未实现")

    async def stream_chat(self, messages, **kwargs):
        # async for chunk in self.llm.stream_chat(messages):
        #     yield chunk
        raise NotImplementedError("Google GenAI stream_chat未实现")

    # 其他能力同理