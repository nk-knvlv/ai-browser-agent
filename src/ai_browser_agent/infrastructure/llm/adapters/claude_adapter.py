from ai_browser_agent.app.ports.llm import LLMPort
from anthropic import Anthropic
from anthropic.types import MessageParam


class ClaudeLLMAdapter(LLMPort):
    def __init__(self, model_name="claude-sonnet-4", api_key=None):
        if not api_key:
            raise Exception('Api key error value')
        self.model_name = model_name
        self.client = Anthropic(api_key=api_key)

    async def send(self, message):
        message = self.client.messages.create(
            model=self.model_name,
            max_tokens=1000,
            messages=[
                MessageParam(
                    role="user",
                    content=message
                )
            ]
        )
        return message.content

    async def test(self):
        message = self.client.messages.create(
            model=self.model_name,
            max_tokens=1000,
            messages=[
                MessageParam(
                    role="user",
                    content="return only one word True if you work normal"
                )
            ]
        )
        if message.content == 'True':
            return True
        raise Exception(message)

    async def close(self):
        self.client.close()
