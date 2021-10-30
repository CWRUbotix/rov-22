class Decorator:
    """
    Adds decorated functions to a list to be used in the dropdown menu for testing
    """

    def __init__(self):
        self.function_list = []  # List of functions

    def __call__(self, func):
        self.function_list.append(func)  # Adds decorated functions to list
