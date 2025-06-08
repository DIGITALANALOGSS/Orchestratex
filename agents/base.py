class AgentBase:
    def __init__(self, name, role):
        self.name = name
        self.role = role
    
    def perform_task(self, task, context=None):
        raise NotImplementedError
