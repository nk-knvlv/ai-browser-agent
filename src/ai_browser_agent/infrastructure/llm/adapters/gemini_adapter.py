from ai_browser_agent.app.ports.llm import LLMPort
from google.genai import Client, types


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
            model=self.model_name,
            contents=message,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=-1)
            ),
        )
        return response.text

    async def test(self):
        response = self.client.models.generate_content(
            model=self.model_name,
            contents='return only one word True if you work normal',
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            ),
        )
        if response.text == 'True':
            return True
        raise Exception(response)

    async def close(self):
        self.client.close()
