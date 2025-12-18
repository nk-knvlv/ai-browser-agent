from ai_browser_agent.domain.services.task_service import TaskService
from ai_browser_agent.infrastructure.browser.adapters.playwright_adapter import PlaywrightBrowserAdapter
from ai_browser_agent.infrastructure.llm.adapters.gemini_adapter import GeminiLLMAdapter
from ai_browser_agent.presentation.cli import CLI

from ai_browser_agent.agent import AIAgent

from os import getenv
from dotenv import load_dotenv


async def main():
    load_dotenv()

    api_key = getenv('API_KEY_GEMINI')
    if not api_key:
        raise ValueError("API_KEY не найден в переменных окружения")

    # infrastructure
    llm_adapter = GeminiLLMAdapter(api_key=api_key)
    await llm_adapter.test()

    browser_adapter = PlaywrightBrowserAdapter(llm_adapter=llm_adapter)

    # run browser
    # await browser_adapter.launch()

    # presentation
    cli = CLI()

    agent = AIAgent(browser_adapter=browser_adapter, llm_adapter=llm_adapter)

    task_service = TaskService(
        agent=agent,
        cli=cli,
    )

    await task_service.run()
