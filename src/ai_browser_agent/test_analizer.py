from typing import Dict, Any, List, Optional
from playwright.async_api import Page
import asyncio
from browser import Browser
from llm import LLM


class AIDOMSearch:
    def __init__(self, page: Page, ai_client):
        self.page = page
        self.ai_client = ai_client  # Клиент для работы с ИИ (OpenAI и т.д.)
        self.visited_selectors = set()
        self.search_stack = []
        self.max_depth = 3
        self.max_branches = 5  # Максимальное количество ветвей для исследования

    async def find_element_by_description(self, description: str) -> str:
        """
        Основная функция для поиска элемента по описанию
        """
        print(f"🔍 Поиск элемента: {description}")

        # Начинаем с body
        self.search_stack = ['body']
        self.visited_selectors = set()

        return await self._search_recursive(description)

    async def _search_recursive(self, description: str, current_depth: int = 0) -> str:
        """
        Рекурсивный поиск с использованием ИИ
        """
        if current_depth >= self.max_depth or not self.search_stack:
            raise Exception("Элемент не найден в пределах максимальной глубины")

        current_selector = self.search_stack[-1]

        # Получаем структуру DOM для текущего селектора
        dom_structure = await self.analyze_dom_structure(current_selector)

        # Анализируем структуру с помощью ИИ
        analysis_result = await self._ask_ai_to_analyze(dom_structure, description, self.search_stack)

        # Если ИИ нашел точный селектор
        if analysis_result.get('found_selector'):
            found_selector = analysis_result['found_selector']
            print(f"✅ Найден селектор: {found_selector}")
            return found_selector

        # Получаем рекомендации по дальнейшему поиску
        next_selectors = analysis_result.get('next_selectors', [])

        # Фильтруем уже посещенные селекторы
        next_selectors = [sel for sel in next_selectors if sel not in self.visited_selectors]

        if not next_selectors:
            # Если нет рекомендаций, возвращаемся на уровень выше
            if len(self.search_stack) > 1:
                self.search_stack.pop()
                return await self._search_recursive(description, current_depth)
            else:
                raise Exception("Элемент не найден")

        # Исследуем рекомендованные селекторы
        for selector in next_selectors[:self.max_branches]:
            try:
                print(f"🔍 Исследую: {selector}")
                self.visited_selectors.add(selector)
                self.search_stack.append(selector)

                # Рекурсивный поиск в этой ветке
                result = await self._search_recursive(description, current_depth + 1)
                if result:
                    return result

                # Если не нашли, убираем из стека и продолжаем
                self.search_stack.pop()

            except Exception as e:
                print(f"❌ Ошибка при исследовании {selector}: {e}")
                if selector in self.search_stack:
                    self.search_stack.pop()
                continue

        # Если ни одна ветка не дала результата, возвращаемся назад
        if len(self.search_stack) > 1:
            self.search_stack.pop()
            return await self._search_recursive(description, current_depth)

        raise Exception("Элемент не найден")

    async def _ask_ai_to_analyze(self, dom_structure: Dict, description: str, search_stack: List[str]) -> Dict[
        str, Any]:
        """
        Запрос к ИИ для анализа DOM структуры и поиска элемента
        """
        prompt = self._create_analysis_prompt(dom_structure, description, search_stack)

        try:
            response = await self.ai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )

            return self._parse_ai_response(response.choices[0].message.content)

        except Exception as e:
            print(f"Ошибка при запросе к ИИ: {e}")
            return {"next_selectors": []}

    def _create_analysis_prompt(self, dom_structure: Dict, description: str, search_stack: List[str]) -> str:
        """
        Создание промпта для ИИ
        """
        current_path = " -> ".join(search_stack)

        prompt = f"""
        Ты - AI помощник для поиска элементов на веб-странице. 

        ЗАДАЧА: Найти элемент по описанию: "{description}"

        ТЕКУЩИЙ ПУТЬ: {current_path}

        СТРУКТУРА DOM:
        {self._format_dom_structure(dom_structure)}

        ПРОШЛЫЕ ВЫБОРЫ: {list(self.visited_selectors)[-5:]}  # Последние 5 посещенных

        ИНСТРУКЦИИ:
        1. Проанализируй структуру DOM выше
        2. Если видишь элемент, который точно соответствует описанию "{description}", верни его селектор
        3. Если точного соответствия нет, выбери 3-5 наиболее перспективных дочерних элементов для дальнейшего исследования
        4. Приоритет отдавай элементам, которые могут содержать input, form, search-поля
        5. Учитывай видимость элементов (visible: true)

        ФОРМАТ ОТВЕТА (JSON):
        {{
            "reasoning": "Краткое объяснение выбора",
            "found_selector": "css_selector или null",
            "next_selectors": ["selector1", "selector2", ...]
        }}

        Пример для поиска поискового поля:
        {{
            "reasoning": "В header есть form с input type='search', это вероятно поисковое поле",
            "found_selector": "header form input[type='search']",
            "next_selectors": []
        }}

        Пример для продолжения поиска:
        {{
            "reasoning": "В main есть несколько section, нужно исследовать те, что содержат формы",
            "found_selector": null,
            "next_selectors": ["main > section:nth-child(1)", "main > div.search-container"]
        }}
        """

        return prompt

    def _format_dom_structure(self, dom_structure: Dict) -> str:
        """
        Форматирование DOM структуры для промпта
        """

        def format_recursive(structure, indent=0):
            lines = []
            prefix = "  " * indent

            # Основная информация об элементе
            selector = structure.get('selector', 'unknown')
            visible = structure.get('visible', False)
            text = structure.get('text', '')
            children_count = structure.get('children_count', {})

            lines.append(f"{prefix}{selector} (visible: {visible}, text: '{text[:50]}...')")

            # Дети
            children = structure.get('children', {})
            for child_tag, child_data in children.items():
                child_visible = child_data.get('visible', False)
                child_text = child_data.get('text', '')[:30]
                child_children = child_data.get('children_count', 0)

                lines.append(
                    f"{prefix}  └── {child_tag} (visible: {child_visible}, text: '{child_text}...', children: {child_children})")

                # Рекурсивно добавляем детей следующего уровня (ограниченно)
                if indent < 1 and 'children' in child_data:
                    grand_children = child_data['children'].get('children', {})
                    for grand_tag, grand_data in grand_children.items():
                        if isinstance(grand_data, dict):
                            grand_visible = grand_data.get('visible', False)
                            lines.append(f"{prefix}      └── {grand_tag} (visible: {grand_visible})")

            return "\n".join(lines)

        return format_recursive(dom_structure)

    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """
        Парсинг ответа от ИИ
        """
        try:
            # Пытаемся извлечь JSON из ответа
            import json
            import re

            # Ищем JSON в тексте
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                print(f"⚠️ ИИ вернул не JSON формат: {response}")
                return {"next_selectors": []}

        except Exception as e:
            print(f"Ошибка парсинга ответа ИИ: {e}")
            return {"next_selectors": []}

    async def analyze_dom_structure(self, selector: str) -> Dict[str, Any]:
        """
        Анализ DOM структуры для указанного селектора
        """
        try:
            structure = await self.page.locator(selector).first.evaluate('''(element) => {
                const result = {
                    selector: element.tagName.toLowerCase(),
                    attributes: {},
                    text: element.textContent ? element.textContent.trim().slice(0, 100) : null,
                    visible: element.offsetWidth > 0 && element.offsetHeight > 0,
                    children: {},
                    children_count: {}
                };

                // Собираем основные атрибуты
                for (let attr of element.attributes) {
                    result.attributes[attr.name] = attr.value;
                }

                // Анализируем непосредственных детей
                const children = element.children;
                const childrenByTag = {};

                for (let child of children) {
                    const tagName = child.tagName.toLowerCase();
                    if (!childrenByTag[tagName]) {
                        childrenByTag[tagName] = [];
                    }
                    childrenByTag[tagName].push(child);
                }

                // Сохраняем количество детей по тегам
                for (let tagName in childrenByTag) {
                    result.children_count[tagName] = childrenByTag[tagName].length;
                }

                // Для каждого типа тега сохраняем информацию о первом ребенке
                for (let tagName in childrenByTag) {
                    if (childrenByTag[tagName].length > 0) {
                        const firstChild = childrenByTag[tagName][0];
                        result.children[tagName] = {
                            selector: tagName,
                            attributes: {},
                            text: firstChild.textContent ? firstChild.textContent.trim().slice(0, 50) : null,
                            visible: firstChild.offsetWidth > 0 && firstChild.offsetHeight > 0,
                            children_count: firstChild.children.length
                        };

                        // Собираем атрибуты для примера ребенка
                        for (let attr of firstChild.attributes) {
                            result.children[tagName].attributes[attr.name] = attr.value;
                        }

                        // Добавляем информацию о детях второго уровня (ограниченно)
                        if (firstChild.children.length > 0) {
                            result.children[tagName].children = {};
                            const grandChildrenByTag = {};

                            for (let grandChild of firstChild.children) {
                                const grandTag = grandChild.tagName.toLowerCase();
                                grandChildrenByTag[grandTag] = (grandChildrenByTag[grandTag] || 0) + 1;
                            }

                            result.children[tagName].children_count = grandChildrenByTag;

                            // Добавляем первого ребенка каждого типа
                            for (let grandTag in grandChildrenByTag) {
                                const firstGrandChild = firstChild.querySelector(grandTag);
                                if (firstGrandChild) {
                                    result.children[tagName].children[grandTag] = {
                                        selector: grandTag,
                                        visible: firstGrandChild.offsetWidth > 0 && firstGrandChild.offsetHeight > 0,
                                        text: firstGrandChild.textContent ? firstGrandChild.textContent.slice(0, 30) : null
                                    };
                                }
                            }
                        }
                    }
                }

                return result;
            }''')

            return structure

        except Exception as e:
            return {"error": str(e), "selector": selector}


# Запуск

async def main():
    description = "кнопка 'Добавить в корзину' для любого товара с помидорами"
    browser = Browser()
    llm = LLM(model_name='gemini-2.5-flash')
    page = await browser.launch(llm)
    await browser.open_url(url="https://samokat.ru")
    print('жду пока страница загрузится')
    selector = await browser.get_element_selector_by_description(description=description)
    print(selector)


if __name__ == "__main__":
    asyncio.run(main())
