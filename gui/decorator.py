class Decorator():
    def __init__(self):
        self.function_list = []

    def __call__(self, func):
        self.function_list.append(func)