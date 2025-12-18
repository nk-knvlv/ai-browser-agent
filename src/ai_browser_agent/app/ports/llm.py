from abc import ABC, abstractmethod
from typing import Protocol


class LLMPort(Protocol):
    """Абстрактный порт для работы с браузером"""
    model_name:str
    api_key:str

    async def send(self, message: str) -> str:
        """Отправляет запрос llm и получает ответ"""
        pass

    async def close(self):
        """Закрывает соединение с клиентом llm"""
        pass

    async def test(self)->bool:
        pass