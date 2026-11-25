# Partie 4 - Question 3 : Builder pour les voitures (options)
class Car:
    def __init__(self):
        self.options = []

    def add(self, option):
        self.options.append(option)

    def __str__(self):
        return "Car(%s)" % ", ".join(self.options)


class CarBuilder:
    def __init__(self):
        self.car = Car()

    def build_base(self):
        for o in ("moteur", "4 roues", "carrosserie"):
            self.car.add(o)
        return self

    def build_air_conditioning(self):
        self.car.add("climatisation"); return self

    def build_gps(self):
        self.car.add("GPS"); return self

    def build_sunroof(self):
        self.car.add("toit ouvrant"); return self

    def build_leather_seats(self):
        self.car.add("sieges en cuir"); return self

    def get_result(self):
        return self.car


class CarDirector:
    def __init__(self, builder):
        self.builder = builder

    def basic_car(self):
        return self.builder.build_base().get_result()

    def full_car(self):
        return (self.builder.build_base().build_air_conditioning()
                .build_gps().build_sunroof().build_leather_seats()
                .get_result())


if __name__ == "__main__":
    print("Basique  :", CarDirector(CarBuilder()).basic_car())
    print("Complete :", CarDirector(CarBuilder()).full_car())
    custom = (CarBuilder().build_base().build_gps()
              .build_air_conditioning().get_result())
    print("Commande personnalisee :", custom)
