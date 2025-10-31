import os
from enum import Enum

from pydantic import SecretStr


class ProviderEnum(str, Enum):
    """支持的 LLM 服务商"""
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    TONGYI = "tongyi"

class LLMFactory(object):

    @staticmethod
    def get_llm(provider: ProviderEnum, model: str = None, **kwargs):
        if provider == ProviderEnum.DEEPSEEK:
            from langchain_deepseek import ChatDeepSeek
            api_key = os.getenv("DEEPSEEK_API_KEY")
            model = model or "deepseek-chat"
            return ChatDeepSeek(
                api_key=SecretStr(api_key),
                model=model,
                streaming=True,
                **kwargs
            )

        elif provider == ProviderEnum.OPENAI:
            from langchain_openai import ChatOpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            model = model or "gpt-3.5-turbo"
            return ChatOpenAI(
                api_key=SecretStr(api_key),
                model=model,
                streaming=True,
                **kwargs
            )

        elif provider == ProviderEnum.TONGYI:
            from langchain_community.llms import Tongyi
            api_key = os.getenv("DASHSCOPE_API_KEY")
            model = model or "qwen-turbo"
            return Tongyi(
                api_key=SecretStr(api_key),
                model=model,
                streaming=True,
                **kwargs
            )
        else:
            raise ValueError(f"不支持的 LLM 服务商: {provider}")
