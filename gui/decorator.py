class Decorator:
    """
    Tracks decorated functions to be used in the dropdown menu for testing
    """

    def __init__(self):
        self.func_dictionary = dict()

    def __call__(self, func):
        self.func_dictionary[func.__name__] = func
