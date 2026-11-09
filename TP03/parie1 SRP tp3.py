class Order:
    def __init__(self, items):
        self.items = items

    def calculate_total(self):
        return sum(item['price'] for item in self.items)

class OrderPrinter:
    def print_order(self, order):
        print("Détails de la commande :")
        for item in order.items:
            print(f"{item['name']}: ${item['price']}")

class OrderRepository:
    def save_to_db(self, order):
        print("Sauvegarde de la commande dans la base de données...")

if __name__ == '__main__':
    products = [
        {"name": "fruit", "price": 50},
        {"name": "vegetables", "price": 100},
        {"name": "Bread", "price": 20},
        {"name": "Meat", "price": 1000},
    ]
    my_order = Order(products)
    printer = OrderPrinter()
    repository = OrderRepository()

    print("Total commande :", my_order.calculate_total(), "$")
    printer.print_order(my_order)
    repository.save_to_db(my_order)
