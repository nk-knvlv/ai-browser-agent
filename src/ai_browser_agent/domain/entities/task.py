class Task:
    """
    Wrapper class for the task
    """
    def __init__(self, description:str):
        self.description = description
        self.plan = None
        self.step = None

    def get_context(self):
        context = {
            "task": self.description,
            "step": self.step,
            "step_history": [],
        }
        return context

