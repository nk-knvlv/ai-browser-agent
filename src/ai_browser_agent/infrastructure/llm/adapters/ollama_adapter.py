from ai_browser_agent.app.ports.llm import LLMPort
import ollama
import asyncio


class OllamaLLMAdapter(LLMPort):
    def __init__(self, model_name="qwen2.5:14b", host="http://localhost:11434"):
        self.model_name = model_name
        self.host = host
        self.client = ollama.Client(host=host)

    async def send(self, message):
        # Ollama работает синхронно, используем run_in_executor
        loop = asyncio.get_event_loop()

        # Правильный способ - передаем функцию и все аргументы в одном словаре или отдельно
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": message}],
                options={
                    "num_predict": 1000,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_gpu": 1,
                    "num_thread": 8
                }
            )
        )

        return response["message"]["content"]

    async def test(self):
        loop = asyncio.get_event_loop()

        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": "return only one word True if you work normal"
                    }
                ],
                options={
                    "num_predict": 10,
                    "temperature": 0
                }
            )
        )

        content = response["message"]["content"].strip().lower()
        if "true" in content:
            return True
        raise Exception(f"Test failed: {content}")

    async def close(self):
        # Ollama клиент не требует явного закрытия
        pass
