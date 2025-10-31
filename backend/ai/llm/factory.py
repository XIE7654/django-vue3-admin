from .adapter.deepseek import DeepSeekAdapter
from .adapter.genai import GoogleGenAIAdapter
from .adapter.openai import OpenAIAdapter
from .adapter.tongyi import TongYiAdapter
from .enums import LLMProvider


def get_adapter(provider: LLMProvider, api_key, model, **kwargs):
    if provider == LLMProvider.DEEPSEEK:
        return DeepSeekAdapter(api_key, model, **kwargs)
    elif provider == LLMProvider.TONGYI:
        return TongYiAdapter(api_key, model, **kwargs)
    elif provider == LLMProvider.OPENAI:
        return OpenAIAdapter(api_key, model, **kwargs)
    elif provider == LLMProvider.GOOGLE_GENAI:
        return GoogleGenAIAdapter(api_key, model, **kwargs)
    else:
        raise ValueError('不支持的服务商')

#  使用示例
# adapter = get_adapter(LLMProvider.TONGYI, api_key='xxx', model='wanx_v1')

# 对话
# try:
#     result = await adapter.chat(messages)
# except NotImplementedError:
#     print("该服务商不支持对话能力")

# # 图片生成
# try:
#     task = adapter.create_image_task(prompt="一只猫")
#     status = adapter.fetch_image_task_status(task)
#     result = adapter.fetch_image_result(task)
# except NotImplementedError:
#     print("该服务商不支持图片生成")