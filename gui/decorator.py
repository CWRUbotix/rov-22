class Decorator:
    """
    Tracks decorated functions to be used in the dropdown menu for testing
    """

    def __init__(self):
        self.func_dictionary = dict()

    def __call__(self, name):
        def decorator(func):
            self.func_dictionary[name] = func
            return func

        return decorator
