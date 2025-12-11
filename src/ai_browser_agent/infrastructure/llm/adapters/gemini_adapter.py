from ai_browser_agent.app.ports.llm import LLMPort
from google.genai import Client


class GeminiLLMAdapter(LLMPort):
    def __init__(self, model_name="gemini-2.5-flash", api_key=None):
        if not api_key:
            raise Exception('Api key error value')
        self.model_name = model_name
        self.client = Client(
            api_key=api_key
        )

    async def send(self, message):
        response = self.client.models.generate_content(
            model=self.model_name, contents=message
        )
        return response.text

    async def test(self):
        response = self.client.models.generate_content(
            model=self.model_name, contents='what is tests for project'
        )
        return response.text

    async def close(self):
        self.client.close()
