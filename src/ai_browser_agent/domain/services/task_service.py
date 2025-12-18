import inspect

from ai_browser_agent.domain.entities.task import Task
from ai_browser_agent.domain.entities.action import Action
from ai_browser_agent.agent import AIAgent
from ai_browser_agent.presentation.cli import CLI


class TaskService:
    """
    Class for task lifecycle management
    """

    def __init__(self, agent: AIAgent, cli: CLI):
        self.agent = agent
        self.cli = cli

    async def run(self):
        try:
            browser_status = self.agent.browser.test()
            model_status = await self.agent.llm.test()

            # begin chat
            self.cli.start_chat(
                browser_status=browser_status,
                model_status=model_status
            )

            task = await self.get_task_from_user()
            await self.solve(task)

        except Exception as e:
            print(f"Критическая ошибка в чате: {e}")

    async def get_task_from_user(self) -> Task:
        task = None
        while not task:
            self.cli.show_message('Какое задание мне выполнить?')
            # Асинхронный ввод вместо блокирующего input()
            message = await self.cli.get_user_input()

            if not message.strip():
                continue  # Пропускаем пустые сообщения

            with CLI.thought_screensaver():
                task = await self.extract_task(message)
                if not task:
                    self.cli.show_message("Пожалуйста, отправьте четкое задание для выполнения")
        task = Task(
            description=task
        )
        return task

    async def extract_task(self, message: str) -> str | None:
        """
        Пытается извлечь задачу из сообщения пользователя.

        Args:
            message: Сообщение от пользователя

        Returns:
            str: Переформулированная задача если найдена
            None: Если задача не найдена или произошла ошибка
        """
        prompted_message = f"""
                    Ты - анализатор задач. Определи, является ли сообщение пользователя задачей для ИИ-ассистента.

                    КРИТЕРИИ ЗАДАЧИ ДЛЯ ИИ:
                    - Конкретное цифровое действие (найти, проанализировать, сравнить, заказать, оформить)
                    - Может быть выполнено через браузер, приложения или с передачей контроля пользователю
                    - Имеет четкую цель
                    - старайся сразу перейти на сайт, используй поиск только если не понимаешь какой конкретно сайт нужен
                    - поисковые инпуты не всегда именно input теги, могли стилизовать div, p или textarea

                    ФОРМАТ ОТВЕТА ТОЧНО В ОДНОЙ СТРОКЕ:
                    [ЗАДАЧА|НЕТ]| | описание

                    Примеры:
                    ЗАДАЧА| Найти рецепт пасты карбонара
                    ЗАДАЧА| Пометь спорные письма как спам на mail
                    НЕТ| Это физическое действие, требующее человека
                    НЕТ| Это приветствие, а не задача
                    ЗАДАЧА| Сравнить цены на iPhone в разных магазинах

                    Сообщение: "{message}"
            """

        try:
            response = await self.agent.llm.send(prompted_message)
            response = response.strip()

            # Разбираем ответ по формату
            if "|" in response:
                parts = response.split("|", 1)
                if len(parts) == 2:
                    status, task_text = parts[0].strip(), parts[1].strip()

                    if status == "ЗАДАЧА" and task_text:
                        return task_text

            return None

        except Exception as e:
            print(f"Ошибка при извлечении задачи из '{message}': {e}")
            return None

    async def solve_task(self, task:Task):
        """
        Алгоритм решения задачи
        """
        # получаем план действий
        with CLI.thought_screensaver(text='Making plan'):
            plan = await self.agent.get_plan(task)
            task.plan = plan
            self.cli.show_message(f'Plan - \n {"\n".join(plan)}')

        for step in task.plan:
            task.step = step
            self.cli.show_message(f'Step - {step}')
            await self.solve_step(step=step, context=task.get_context())


    async def solve_step(self, step, context):
        attempt = 0
        while attempt < 4:
            try:
                attempt += 1
                self.cli.show_message(f'Выполняю - {step}')
                response = await self.agent.get_step_actions_info(context)

                if 'thought' in response:
                    self.cli.show_message(f'Мысли - {response['thought']}')

                if response['actions'] == 'success':
                    break
                if response['actions'] == 'wait_for_the_human':
                    await self.wait_human(favour=response['thought'])
                    break
                await self.execute_actions(actions=response['actions'])

            except Exception as e:
                print(f"Ошибка при выполнении шага {step} сообщения: {e}")
                continue
        raise Exception("Не получилось выполнить задание за отведенные попытки")

    async def execute_actions(self, actions:list[Action]):
        for action in actions:
            self.cli.show_message(f'выполняю {action}')

            method = getattr(self.agent.browser, action.name, None)
            try:
                with CLI.thought_screensaver(text=f'Execute {action.name}'):
                    if inspect.iscoroutinefunction(method):
                        returned = await method(**action.parameters)
                    else:
                        returned = method(**action.parameters)

            except AttributeError:
                error_msg = f"Method  not found in Browser"
                print(error_msg)

            except TypeError as e:
                error_msg = f"Invalid parameters for {action.name}: {e}"
                print(error_msg)

            except Exception as e:
                error_msg = f"Unexpected error in {action.name}: {e}"
                print(error_msg)

    async def wait_human(self, favour):
        self.cli.show_message(favour)
        favour_is_responding = False

        while not favour_is_responding:
            message = await self.cli.get_user_input()
            prompt = f"""Если в сообщении пользователь подтвердил что выполнил то о чем его попросили,
             или написал что ты можешь продолжать, то отправь True, если нет отправь False
             сообщение пользователя:{message}
            """

            response = await self.agent.llm.send(prompt)
            if response == "True":
                favour_is_responding = True

