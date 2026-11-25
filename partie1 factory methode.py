# Partie 1 - Factory Method : ShapeFactory_SCT et ShapeFactory_SCR
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def draw(self): ...
    @abstractmethod
    def erase(self): ...


class Circle(Shape):
    def draw(self): print("Circle.draw")
    def erase(self): print("Circle.erase")


class Square(Shape):
    def draw(self): print("Square.draw")
    def erase(self): print("Square.erase")


class Triangle(Shape):
    def draw(self): print("Triangle.draw")
    def erase(self): print("Triangle.erase")


class Rectangle(Shape):
    def draw(self): print("Rectangle.draw")
    def erase(self): print("Rectangle.erase")


class ShapeFactory(ABC):
    @abstractmethod
    def createShape(self, type): ...


class ShapeFactory_SCT(ShapeFactory):
    """Square, Circle, Triangle uniquement."""
    def createShape(self, type):
        if type == "Circle":
            return Circle()
        elif type == "Square":
            return Square()
        elif type == "Triangle":
            return Triangle()
        print("ShapeFactory_SCT : forme non supportee -> " + type)
        return None


class ShapeFactory_SCR(ShapeFactory):
    """Square, Circle, Rectangle uniquement."""
    def createShape(self, type):
        if type == "Circle":
            return Circle()
        elif type == "Square":
            return Square()
        elif type == "Rectangle":
            return Rectangle()
        print("ShapeFactory_SCR : forme non supportee -> " + type)
        return None


if __name__ == "__main__":
    for factory in (ShapeFactory_SCT(), ShapeFactory_SCR()):
        print("=====", factory.__class__.__name__, "=====")
        for type in ("Circle", "Square", "Triangle", "Rectangle"):
            shape = factory.createShape(type)
            if shape:
                shape.draw()
                shape.erase()