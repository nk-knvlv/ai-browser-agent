import json
from http.client import responses
from json import dumps
import inspect
from ai_browser_agent.app.ports.browser import BrowserPort
from ai_browser_agent.app.ports.llm import LLMPort


class AIAgent:
    """
    Класс ИИ агента выполняющего задания в браузере
    """

    def __init__(self, browser_adapter: BrowserPort, llm_adapter: LLMPort):
        self.browser = browser_adapter
        self.llm = llm_adapter





    async def send(self, message) -> str:
        """
        Обрабатывает сообщение от пользователя
        """
        self.cli.show_message('Думаю...')
        await self.browser.wait(2000)
        response = await self.llm.send(message)
        return response

    def update_context(self, context):
        for el, val in context.items():
            self.context[el] = val

    async def get_plan(self, task)->list:
        """
        Создает последовательность из высокоуровневых шагов для решения задачи
        Args:
            task:

        Returns:

        """
        plan_making_prompt = f"""
            Ты - автономный AI-агент, который управляет веб-браузером для выполнения задач пользователя.
            
            Ты получишь задачу от пользователя и класс для взаимодействия с браузером
            
            Начинаешь ты с about:blank страницы
            Ты должен анализировать HTML, чтобы понять, какие элементы присутствуют на странице,
            и решить, какое действие выполнить next.
            Ты должен быть осторожен и не выполнять действия, которые могут навредить.
            Ты можешь выполнять поиск в поисковых системах. 
            Если действие подразумевает данные или подтверждения которые знает только человек,
            например выбор адреса или внесение данных оплаты,
            тебе нужно передать управление человеку.
            
            
            Пользователь хочет: {task}.
            
            Разбей эту задачу на высокоуровневые односложные, но информативные шаги. Например:
            
            ["Открыть сайт mail.ru", "Прочитать письма", "Если спам то пометить как спам"]
            Далее переведи его в json
            ВАЖНО: Возвращай только чистый json без каких-либо обратных кавычек, маркеров кода или пояснений.
            """
        json_plan = await self.send(plan_making_prompt)
        return json.loads(json_plan)

    @staticmethod
    def get_class_func_description(cls: BrowserPort) -> str:
        """
        Получает описание всех методов класса.

        Args:
            cls: Класс для анализа

        Returns:
            str: JSON-строка с информацией о всех методах класса
        """
        functions_info = []

        # Получаем все методы класса
        for func_name, func in inspect.getmembers(cls, predicate=inspect.iscoroutinefunction):
            # Пропускаем приватные и защищенные методы
            if func_name.startswith('_'):
                continue

            # Получаем сигнатуру
            signature = inspect.signature(func)
            parameters = []

            for param_name, param in signature.parameters.items():
                if param_name in ('self', 'cls'):
                    continue

                param_info = {"name": param_name}

                if param.annotation != inspect.Parameter.empty:
                    param_info["type"] = str(param.annotation)

                if param.default != inspect.Parameter.empty:
                    param_info["default"] = str(param.default)

                parameters.append(param_info)

            func_info = {
                "name": func_name,
                "parameters": parameters,
                "return_type": str(signature.return_annotation),
            }

            functions_info.append(func_info)

        return dumps(functions_info, ensure_ascii=False, indent=2)

    async def get_step_actions_info(self, context):
        context['current_url'] = self.browser.page
        available_actions = self.get_class_func_description(self.browser)
        prompt = f"""
                Ты - автономный AI-агент, который управляет веб-браузером для выполнения задач пользователя.

                Учитывая контекст, проверь выполнена ли задача, если нет то сгенерируй последовательность действий для выполнения текущего шага.
                Если ты не знаешь нужный селектор для действия сначала найди его с помощью доступных методов
              
                Если это действие подразумевает загрузку как например переход на новую страницу или поиск с ожиданием элемента, в список действий добавь действие ожидания 
                
                КОМАНДА: Возвращай ТОЛЬКО данные в виде Json. НИКАКИХ обратных кавычек, НИКАКИХ комментариев или пояснений.
                
                СТРУКТУРА ОТВЕТА:
                {{
                    "thought": "объяснение что видишь и почему выбираешь действие",
                    "actions": [массив действий или строка],
                    "context": {{'измененные поля контекста'}}
                }}
                
                ПРАВИЛА:
                - Используй только доступные действия
                - Для авторизации/оплаты используй "wait_for_the_human"
                - Указывай в контексте только измененные поля
                
        
               
                возвращай в таком виде:
               
                - "thought": строка, в которой ты объясняешь, что ты видишь на странице и почему ты выбираешь следующее действие.
                - "actions": объект, описывающий действия. Если ты решил выполнить функцию, то укажи имя функции и аргументы. Если текущая подзадача завершена, то в "actions" вместо массива укажи строку success. 
                - "context": объект, описывающий контекст. Если ты в действии перешел на другой сайт соответствующе поменяй контекст. Указывай только те поля которые поменялись.
                
                Если подзадача это авторизация или оплата, то в "actions" вместо массива укажи строку wait_for_the_human
                            
               Пример ответа:
                "thought": "я понимаю что нахожусь не на том сайте где пользователь просил решить задачу, надо перейти на нужный",
                   "actions":{{
                               {{
                                   "name": "open_url",
                                   "parameters": {{
                                           "url": "https://samokat.ru",
                                   }}
                               }},
                               {{
                                   "name": "type",
                                   "parameters": {{
                                           "selector": "input[.search]",
                                           "text": "мед",
                                   }}
                               }}
                           }},
                   "context":{{
                       "current_url": "https://samokat.ru",
                   }}

               контекст:    
               {dumps(context, ensure_ascii=False)} 
               
                Доступные
                действия:
                {available_actions}

               """
        response = json.dumps(await self.send(prompt))
        return response
