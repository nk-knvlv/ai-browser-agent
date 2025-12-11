from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Page(ABC):
    """Абстрактное представление веб-страницы"""


class BrowserPort(ABC):
    """Абстрактный порт для работы с браузером"""

    @abstractmethod
    def _launch(self) -> Page:
        pass

    @abstractmethod
    def _stop(self) -> Page:
        pass

    @abstractmethod
    async def click(self, selector: str) -> Page:
        """Кликнуть по элементу и получить новую страницу"""
        pass

    @abstractmethod
    async def new_page(self, selector: str) -> Page:
        """Кликнуть по элементу и получить новую страницу"""
        pass

    @abstractmethod
    async def get_page_url(self, selector: str) -> Page:
        """Кликнуть по элементу и получить новую страницу"""
        pass

    @abstractmethod
    async def open_url(self, selector: str) -> Page:
        """Кликнуть по элементу и получить новую страницу"""
        pass

    @abstractmethod
    async def type_into(self, selector: str) -> Page:
        """Кликнуть по элементу и получить новую страницу"""
        pass

    @abstractmethod
    async def wait(self, selector: str) -> Page:
        """Кликнуть по элементу и получить новую страницу"""
        pass

    @abstractmethod
    async def press(self, selector: str) -> Page:
        """Кликнуть по элементу и получить новую страницу"""
        pass


    @abstractmethod
    async def _glimpse_scan(self, selector: str) -> Page:
        """Кликнуть по элементу и получить новую страницу"""
        pass


    @abstractmethod
    async def _analyze_dom_structure(self, selector: str) -> Page:
        """Кликнуть по элементу и получить новую страницу"""
        pass


    @abstractmethod
    async def get_element_selector_by_description(self, selector: str) -> Page:
        """Кликнуть по элементу и получить новую страницу"""
        pass

