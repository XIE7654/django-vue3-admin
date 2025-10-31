from abc import ABC

class MultiModalAICapability(ABC):
    # 对话能力
    async def chat(self, messages, **kwargs):
        raise NotImplementedError("chat not supported by this provider")

    async def stream_chat(self, messages, **kwargs):
        raise NotImplementedError("stream_chat not supported by this provider")

    # 图片生成能力
    def create_drawing_task(self, prompt: str, style='watercolor', size='1024*1024', n=1, **kwargs):
        raise NotImplementedError("drawing generation not supported by this provider")

    def fetch_drawing_task_status(self, task):
        raise NotImplementedError("drawing task status not supported by this provider")

    def fetch_drawing_result(self, task):
        raise NotImplementedError("drawing result not supported by this provider")

    # 视频生成能力
    def create_video_task(self, prompt, **kwargs):
        raise NotImplementedError("video generation not supported by this provider")

    def fetch_video_task_status(self, task):
        raise NotImplementedError("video task status not supported by this provider")

    def fetch_video_result(self, task):
        raise NotImplementedError("video result not supported by this provider")

    # 知识库能力
    def query_knowledge(self, query, **kwargs):
        raise NotImplementedError("knowledge query not supported by this provider")

    # 语音合成能力
    def synthesize_speech(self, text, **kwargs):
        raise NotImplementedError("speech synthesis not supported by this provider")