# Partie 4 - Questions 1 et 2 : Builder pour les sandwichs
from abc import ABC, abstractmethod


class Sandwich:
    def __init__(self):
        self.name = ""
        self.ingredients = []

    def add(self, ingredient):
        self.ingredients.append(ingredient)

    def __str__(self):
        return "%s : %s" % (self.name, ", ".join(self.ingredients))


class SandwichBuilder(ABC):
    def __init__(self):
        self.sandwich = Sandwich()

    @abstractmethod
    def build_bread(self): ...
    @abstractmethod
    def build_main(self): ...
    @abstractmethod
    def build_sauce(self): ...
    @abstractmethod
    def build_extras(self): ...


class ShawarmaBuilder(SandwichBuilder):
    def __init__(self):
        super().__init__()
        self.sandwich.name = "Sandwich Shawarma"
    def build_bread(self): self.sandwich.add("pain pita")
    def build_main(self): self.sandwich.add("poulet shawarma")
    def build_sauce(self): self.sandwich.add("sauce a l'ail")
    def build_extras(self): self.sandwich.add("cornichons")


class GroundMeatBuilder(SandwichBuilder):
    def __init__(self):
        super().__init__()
        self.sandwich.name = "Sandwich viande hachee"
    def build_bread(self): self.sandwich.add("pain baguette")
    def build_main(self): self.sandwich.add("viande hachee")
    def build_sauce(self): self.sandwich.add("harissa")
    def build_extras(self): self.sandwich.add("oignons")


class FriedOmeletBuilder(SandwichBuilder):
    def __init__(self):
        super().__init__()
        self.sandwich.name = "Sandwich frites + omelette"
    def build_bread(self): self.sandwich.add("pain baguette")
    def build_main(self): self.sandwich.add("omelette")
    def build_sauce(self): self.sandwich.add("mayonnaise")
    def build_extras(self): self.sandwich.add("pommes de terre frites")


class SandwichDirector:
    def __init__(self, builder):
        self.builder = builder

    def make(self):
        self.builder.build_bread()
        self.builder.build_main()
        self.builder.build_sauce()
        self.builder.build_extras()
        return self.builder.sandwich


if __name__ == "__main__":
    for b in (ShawarmaBuilder(), GroundMeatBuilder(), FriedOmeletBuilder()):
        print(SandwichDirector(b).make())