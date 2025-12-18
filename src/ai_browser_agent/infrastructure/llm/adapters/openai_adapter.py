from ai_browser_agent.app.ports.llm import LLMPort
from openai import AsyncOpenAI
from typing import Optional


class OpenAILLMAdapter(LLMPort):
    def __init__(self, model_name="gpt-4o", api_key=None):
        if not api_key:
            raise ValueError('API key is required')

        self.model_name = model_name
        self.client = AsyncOpenAI(api_key=api_key, base_url="https://api.zeroeval.com/v1")

    async def send(self, message: str) -> str:
        """Отправка сообщения и получение ответа"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    async def test(self) -> bool:
        """Проверка работоспособности API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                max_tokens=10,
                messages=[
                    {
                        "role": "user",
                        "content": "Return only the word 'True' if you are working properly"
                    }
                ]
            )
            result = response.choices[0].message.content or ""
            return result.strip() == 'True'
        except Exception as e:
            raise Exception(f"OpenAI API test failed: {str(e)}")

    async def close(self):
        """Закрытие клиента (для AsyncOpenAI обычно не требуется)"""
        # AsyncOpenAI не имеет метода close() в текущей версии,
        # но оставляем для совместимости с интерфейсом
        pass

    async def __aenter__(self):
        """Поддержка контекстного менеджера"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Завершение работы в контекстном менеджере"""
        await self.close()
