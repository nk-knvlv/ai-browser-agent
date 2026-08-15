from ai_browser_agent.domain.services.task_service import TaskService
from ai_browser_agent.infrastructure.browser.adapters.playwright_adapter import PlaywrightBrowserAdapter
from ai_browser_agent.infrastructure.llm.adapters.grok_adapter import GroqLLMAdapter
from ai_browser_agent.infrastructure.llm.adapters.ollama_adapter import OllamaLLMAdapter
from ai_browser_agent.presentation.cli import CLI

from ai_browser_agent.agent import AIAgent

from os import getenv
from dotenv import load_dotenv


async def main():
    load_dotenv()

    api_key = getenv('GROK_AI_KEY')
    if not api_key:
        raise ValueError("API_KEY не найден в переменных окружения")


    # infrastructure

    # llm_adapter = OllamaLLMAdapter(api_key=api_key)
    llm_adapter = OllamaLLMAdapter(
        model_name="qwen2.5",  # или "qwen2.5:7b", "qwen2.5:14b"
        host="http://localhost:11434"
    )

    await llm_adapter.test()

    browser_adapter = PlaywrightBrowserAdapter(llm_adapter=llm_adapter)

    # run browser
    await browser_adapter.launch()

    # presentation
    cli = CLI()

    agent = AIAgent(browser_adapter=browser_adapter, llm_adapter=llm_adapter, cli=cli)

    task_service = TaskService(
        agent=agent,
        cli=cli,
    )

    await task_service.run()
