class Discount:
    def __init__(self, price):
        self.price = price

    def apply_discount(self):
        return self.price

class VIPDiscount(Discount):
    def apply_discount(self):
        return self.price * 0.8      # 20 %

class RegularDiscount(Discount):
    def apply_discount(self):
        return self.price * 0.95     # 5 %

# Nouvelle remise : ajoutée SANS modifier le code existant
class FirstTimeDiscount(Discount):
    def apply_discount(self):
        return self.price * 0.9      # 10 %

if __name__ == '__main__':
    price = 1000
    clients = {
        "VIP": VIPDiscount(price),
        "regular": RegularDiscount(price),
        "first time": FirstTimeDiscount(price),
    }
    for customer, discount in clients.items():
        print(f"Ancien prix : {price} pour {customer}, "
              f"nouveau prix : {discount.apply_discount()}")