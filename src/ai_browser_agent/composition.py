from infrastructure.browser.adapters.playwright_adapter import PlaywrightBrowserAdapter
from agent import AIAgent
from infrastructure.llm.adapters.gemini_adapter import GeminiLLMAdapter

from os import getenv
from dotenv import load_dotenv

async def main():
    load_dotenv()

    # infrastructure
    llm_adapter = GeminiLLMAdapter(api_key=getenv('API_KEY'))
    browser_adapter = PlaywrightBrowserAdapter()

    agent = AIAgent(browser_adapter, llm_adapter)

    await agent.start()
