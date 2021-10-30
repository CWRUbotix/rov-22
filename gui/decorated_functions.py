from gui.decorator import Decorator

dropdown = Decorator()

@dropdown
def test():
    print("test")

@dropdown
def test2():
    print("test2")

