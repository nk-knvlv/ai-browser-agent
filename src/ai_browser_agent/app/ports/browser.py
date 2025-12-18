from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol, List


@dataclass
class Page(ABC):
    """Абстрактное представление веб-страницы"""


class BrowserPort(Protocol):
    """Абстрактный порт для работы с браузером"""
    page_context: List[str]

    def __init__(self):
        self.page = None

    async def launch(self) -> Page:
        """Запустить. Метод не для использования ИИ."""
        pass

    async def stop(self) -> Page:
        """Остановить браузер. Метод не для использования ИИ."""
        pass

    def test(self) -> bool:
        """Готов ли браузер к работе. Метод не для использования ИИ."""
        pass

    async def click(self, selector: str) -> Page:
        """Кликнуть по элементу и получить новую страницу"""
        pass

    async def new_page(self, selector: str) -> Page:
        """Кликнуть по элементу и получить новую страницу"""
        pass

    async def get_page_url(self, selector: str) -> Page:
        """Кликнуть по элементу и получить новую страницу"""
        pass

    async def open_url(self, selector: str) -> Page:
        """Кликнуть по элементу и получить новую страницу"""
        pass

    async def type_into(self, selector: str) -> Page:
        """Кликнуть по элементу и получить новую страницу"""
        pass

    async def wait(self, selector: str) -> Page:
        """Кликнуть по элементу и получить новую страницу"""
        pass

    async def press(self, selector: str) -> Page:
        """Кликнуть по элементу и получить новую страницу"""
        pass

    async def _glimpse_scan(self, selector: str) -> Page:
        """Кликнуть по элементу и получить новую страницу"""
        pass

    async def _analyze_dom_structure(self, selector: str) -> Page:
        """Кликнуть по элементу и получить новую страницу"""
        pass

    async def get_element_selector_by_description(self, selector: str) -> Page:
        """Кликнуть по элементу и получить новую страницу"""
        pass
