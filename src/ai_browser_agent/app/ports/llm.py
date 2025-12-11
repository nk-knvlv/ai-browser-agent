from abc import ABC, abstractmethod


class LLMPort(ABC):
    """Абстрактный порт для работы с браузером"""
    api_key:str

    @abstractmethod
    def __init__(self, model_name:str,api_key: str):
        pass

    @abstractmethod
    def send(self, message: str) -> str:
        pass

    @abstractmethod
    def close(self):
        pass
