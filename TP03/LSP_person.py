class Person:
    def __init__(self, name):
        self.name = name

class Employee(Person):
    def get_salary(self):
        return 50000
    def assign_task(self, task):
        print(f"{self.name} reçoit la tâche : {task}")

class Student(Person):
    def get_grades(self):
        return [14, 16, 12]

def show_info(person: Person):          # fonctionne avec tous les sous-types
    print(f"Nom : {person.name}")

def pay(employee: Employee):            # le client demande le bon type
    print(employee.get_salary())

if __name__ == '__main__':
    show_info(Employee("Ali"))
    show_info(Student("Sara"))
    pay(Employee("Ali"))
