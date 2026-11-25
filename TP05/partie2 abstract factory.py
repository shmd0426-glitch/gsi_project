# Partie 2 - Abstract Factory (formes 2D et 3D)
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def draw(self): ...
    @abstractmethod
    def erase(self): ...


class Circle(Shape): pass
class Square(Shape): pass


class Circle2D(Circle):
    def draw(self): print("Circle.draw2D")
    def erase(self): print("Circle.erase2D")


class Circle3D(Circle):
    def draw(self): print("Circle.draw3D")
    def erase(self): print("Circle.erase3D")


class Square2D(Square):
    def draw(self): print("Square.draw2D")
    def erase(self): print("Square.erase2D")


class Square3D(Square):
    def draw(self): print("Square.draw3D")
    def erase(self): print("Square.erase3D")


class ShapeFactory(ABC):
    @staticmethod
    @abstractmethod
    def createShape(type): ...


class ShapeFactory2D(ShapeFactory):
    @staticmethod
    def createShape(type):
        if type == "Circle":
            return Circle2D()
        elif type == "Square":
            return Square2D()
        return None


class ShapeFactory3D(ShapeFactory):
    @staticmethod
    def createShape(type):
        if type == "Circle":
            return Circle3D()
        elif type == "Square":
            return Square3D()
        return None


if __name__ == "__main__":
    print("# 2D objects creation")
    for type in ("Circle", "Square", "Circle", "Square"):
        shape = ShapeFactory2D.createShape(type)
        shape.draw()
        shape.erase()
    print("# 3D objects creation")
    for type in ("Circle", "Square", "Circle", "Square"):
        shape = ShapeFactory3D.createShape(type)
        shape.draw()
        shape.erase()
