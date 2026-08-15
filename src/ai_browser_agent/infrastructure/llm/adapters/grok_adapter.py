from ai_browser_agent.app.ports.llm import LLMPort
from groq import AsyncGroq


class GroqLLMAdapter(LLMPort):
    def __init__(self, model_name="llama-3.3-70b-versatile", api_key=None):
        if not api_key:
            raise Exception('API key is required')
        self.model_name = model_name
        self.client = AsyncGroq(api_key=api_key)

    async def send(self, message):
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": message
                }
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content

    async def test(self):
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": "Return only one word 'True' if you work normally"
                }
            ],
            max_tokens=10
        )
        result = response.choices[0].message.content.strip()
        if result == 'True':
            return True
        raise Exception(f"Test failed: {result}")

    async def close(self):
        # AsyncGroq не требует явного закрытия
        pass