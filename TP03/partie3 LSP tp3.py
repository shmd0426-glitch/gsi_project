class Shape:
    def get_area(self):
        raise NotImplementedError("Doit être implémentée par la sous-classe")

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    def get_area(self):
        return self.width * self.height

class Square(Shape):
    def __init__(self, side_length):
        self.side_length = side_length
    def get_area(self):
        return self.side_length * self.side_length

def print_area(shape):
    print(f"Aire : {shape.get_area()}")

if __name__ == '__main__':
    shapes = [Rectangle(5, 10), Square(5)]
    for s in shapes:
        print_area(s)      # Rectangle -> 50, Square -> 25
