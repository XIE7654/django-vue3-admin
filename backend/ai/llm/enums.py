from enum import Enum


class LLMProvider(str, Enum):
    """LLM 提供商枚举"""
    DEEPSEEK = "deepseek"
    TONGYI = "tongyi"
    OPENAI = "openai"
    GOOGLE_GENAI = "google-genai"
    
    @classmethod
    def get_model_by_platform(cls, platform: str) -> tuple[str, str]:
        """根据平台名称获取对应的模型和API密钥环境变量名"""
        if platform == cls.TONGYI:
            return 'qwen-plus', 'DASHSCOPE_API_KEY'
        elif platform == cls.DEEPSEEK:
            return 'deepseek-chat', 'DEEPSEEK_API_KEY'
        elif platform == cls.OPENAI:
            return 'gpt-3.5-turbo', 'OPENAI_API_KEY'
        elif platform == cls.GOOGLE_GENAI:
            return 'gemini-pro', 'GOOGLE_API_KEY'
        else:
            # 默认使用 DeepSeek
            return 'deepseek-chat', 'DEEPSEEK_API_KEY'
    
    @classmethod
    def from_string(cls, platform: str) -> 'LLMProvider':
        """从字符串创建枚举值，如果不存在则返回默认值"""
        try:
            return cls(platform)
        except ValueError:
            return cls.DEEPSEEK  # 默认返回 DeepSeek 