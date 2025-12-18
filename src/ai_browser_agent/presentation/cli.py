from asyncio import get_event_loop
from contextlib import contextmanager
from yaspin import yaspin

class CLI:
    """
    User Interaction. Receiving a task from the user. Displaying progress and results. Clean UI layer.
    """
    def __init__(self):
        self.loop = get_event_loop()

    @staticmethod
    def show_message(message):
        print(f'Agent: ' + message)


    async def get_user_input(self):
        user_input = await self.loop.run_in_executor(None, input, "▸ ")
        return user_input

    @staticmethod
    def start_chat(browser_status, model_status):
        """
        Запускает интерактивный чат с пользователем.
        """
        start_message = f"""
        ╔══════════════════════════════════════╗
        ║      AUTONOMOUS BROWSER AGENT        ║
        ║           v1.0 | AI-Powered          ║
        ╚══════════════════════════════════════╝
        [STATUS] Браузер: {browser_status}
        [STATUS] AI Модель: {model_status}
        """

        print(start_message)

    @staticmethod
    @contextmanager
    def thought_screensaver(text="loading", final_text=None):
        try:
            with yaspin().arc as sp:
                sp.text = text
                yield  # Здесь выполняется код внутри with
        except Exception as e:
            print(e)
        finally:
            if final_text:
                print(final_text)