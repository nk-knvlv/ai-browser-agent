from playwright.async_api import Page
from typing import Dict, Any, List
from browser import Browser
import asyncio
from llm import LLM

class DOMAnalyzer:
    def __init__(self):
        self.max_depth = 5

    async def analyze_dom_structure(self, page: Page, root_selector: str = 'body', current_depth: int = 0) -> Dict[
        str, Any]:
        """Рекурсивный анализ DOM-структуры с глубиной до 5 уровней"""

        if current_depth >= self.max_depth:
            return {"depth_exceeded": True}

        try:
            structure = await page.locator(root_selector).first.evaluate('''(element, current_depth) => {
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

                // Для каждого типа тега сохраняем первого ребенка как пример
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
                    }
                }

                return result;
            }''', current_depth)

            # Рекурсивно анализируем детей следующего уровня
            for child_tag in list(structure['children'].keys()):
                child_selector = f"{root_selector} > {child_tag}"
                if structure['children_count'].get(child_tag, 0) > 0:
                    try:
                        child_structure = await self.analyze_dom_structure(
                            page, child_selector, current_depth + 1
                        )
                        structure['children'][child_tag]['children'] = child_structure
                    except Exception as e:
                        structure['children'][child_tag]['children'] = {'error': str(e)}

            return structure

        except Exception as e:
            return {"error": str(e), "selector": root_selector, "depth": current_depth}

    async def find_search_input(self, page: Page) -> str:
        """Находит поисковый input на странице используя анализ структуры"""

        # Сначала быстрый поиск по распространенным селекторам
        search_selectors = [
            'input[type="search"]',
            'input[placeholder*="поиск" i]',
            'input[name="search"]',
            'input[name="q"]',
            '[data-testid*="search"] input',
            '.search input',
            '#search input'
        ]

        for selector in search_selectors:
            if await page.locator(selector).count() > 0:
                return selector


        # Ищем секции, которые могут содержать поиск
        potential_sections = []
        for section_type, sections in structure.items():
            for section in sections:
                if section.get('has_input') and section.get('visible'):
                    potential_sections.append(section)

        # Детально анализируем потенциальные секции
        for section in potential_sections:
            section_selector = f"{section['tag']}"
            if section['id']:
                section_selector = f"#{section['id']}"
            elif section['classes']:
                section_selector = f".{section['classes'].split()[0]}"

            # Ищем input в этой секции
            inputs_in_section = await page.locator(f"{section_selector} input").all()
            for input_element in inputs_in_section:
                input_info = await input_element.evaluate('''el => ({
                    type: el.type,
                    placeholder: el.placeholder || '',
                    name: el.name || '',
                    visible: el.offsetWidth > 0 && el.offsetHeight > 0
                })''')

                # Проверяем, похож ли input на поисковый
                if (input_info['visible'] and
                        (input_info['type'] in ['search', 'text'] or
                         'поиск' in input_info['placeholder'].lower() or
                         'search' in input_info['name'].lower())):
                    # Генерируем селектор для этого input
                    input_selector = await self._generate_input_selector(input_element)
                    return input_selector

        raise Exception("Search input not found")

    async def _generate_input_selector(self, input_element) -> str:
        """Генерирует селектор для input элемента"""
        selector_info = await input_element.evaluate('''el => {
            if (el.id) return '#' + el.id;

            const classes = el.className ? el.className.split(' ').filter(c => c.length > 0) : [];
            if (classes.length > 0) {
                return 'input.' + classes[0];
            }

            if (el.name) return `input[name="${el.name}"]`;
            if (el.placeholder) return `input[placeholder*="${el.placeholder.slice(0, 20)}"]`;

            // Поиск по родителям
            let parent = el.parentElement;
            let depth = 0;
            while (parent && depth < 3) {
                if (parent.id) {
                    return `#${parent.id} input`;
                }
                if (parent.className) {
                    const parentClasses = parent.className.split(' ').filter(c => c.length > 0);
                    if (parentClasses.length > 0) {
                        return `.${parentClasses[0]} input`;
                    }
                }
                parent = parent.parentElement;
                depth++;
            }

            return 'input';
        }''')

        return selector_info


# Пример использования
async def find_tomatoes_with_dom_analysis(page: Page):
    analyzer = DOMAnalyzer()

    try:
        # 1. Получаем упрощенную структуру для понимания страницы
        simple_structure = await analyzer.get_simplified_structure(page)
        print("Структура страницы:", simple_structure)

        # 2. Находим поисковый input через анализ
        search_selector = await analyzer.find_search_input(page)
        print(f"Найден поисковый элемент: {search_selector}")

        print("Поиск помидоров выполнен успешно!")
        return True

    except Exception as e:
        print(f"Ошибка при поиске через DOM анализ: {e}")

        # Резервная стратегия
        return await fallback_search(page)


async def fallback_search(page: Page):
    """Резервная стратегия поиска"""
    try:
        # Простой поиск по всем input
        inputs = await page.locator('input[type="text"], input[type="search"]').all()
        for input_element in inputs:
            if await input_element.is_visible():
                await input_element.click()
                await input_element.fill("помидоры")
                await input_element.press("Enter")
                return True
    except Exception as e:
        print(f"Резервный поиск также не удался: {e}")

    return False


async def run():
    # browser = Browser()
    # page = await browser.launch()
    # await browser.open_url('https://samokat.ru/')
    # await find_tomatoes_with_dom_analysis(page)
    #
    llm = LLM()
    result = await llm.test()
    await llm.close()
    print(result)

asyncio.run(run())
