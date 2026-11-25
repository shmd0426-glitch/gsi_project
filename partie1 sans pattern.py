# Partie 1 - Sans Design Pattern (questions 1 et 2 : + triangle et rectangle)
import sys
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


if __name__ == "__main__":
    for type_ in ("Circle", "Square", "Triangle", "Rectangle"):
        if type_ == "Circle":
            shape = Circle()
        elif type_ == "Square":
            shape = Square()
        elif type_ == "Triangle":
            shape = Triangle()
        elif type_ == "Rectangle":
            shape = Rectangle()
        else:
            print("Bad shape creation: " + type_)
            sys.exit()
        shape.draw()
        shape.erase()