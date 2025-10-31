from langchain_community.chat_models import ChatTongyi
from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import requests
from dashscope import ImageSynthesis
import os

from llm.base import MultiModalAICapability


class TongYiAdapter(MultiModalAICapability):
    def __init__(self, api_key, model, **kwargs):
        self.api_key = api_key
        self.model = model
        self.llm = ChatTongyi(api_key=api_key, model=model, streaming=True)

    async def chat(self, messages, **kwargs):
        # 兼容 DeepSeek 的调用方式
        return await self.llm.ainvoke(messages)

    async def stream_chat(self, messages, **kwargs):
        async for chunk in self.llm.astream(messages):
            yield chunk

    def create_drawing_task(self, prompt: str, style='watercolor', size='1024*1024', n=1, **kwargs):
        """创建异步图片生成任务"""
        rsp = ImageSynthesis.async_call(
            api_key=self.api_key,
            model=self.model,
            prompt=prompt,
            n=n,
            style=f'<{style}>',
            size=size
        )
        return rsp

    def fetch_drawing_task_status(self, task):
        """获取异步图片任务状态"""
        rsp = ImageSynthesis.fetch(task, api_key=self.api_key)
        return rsp


    