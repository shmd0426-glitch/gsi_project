from academicelement import AcademicElement
from module import Module


class Unit(AcademicElement):
    def __init__(self, name, title, modules=None):
        super().__init__(name, title)
        self._modules = []
        for m in (modules or []):
            self.add_module(m)

    def add_module(self, module):
        self._modules.append(module)
        # agrégation des attributs
        self.coef += module.coef
        self.credit += module.credit
        self.hours_lecture += module.hours_lecture
        self.hours_td += module.hours_td
        self.hours_tp += module.hours_tp

    def find_module(self, code):
        return next((m for m in self._modules if m.name == code), None)

    def calculate_average(self):
        if not self._modules:
            return 0
        total = sum(m.calculate_average() * m.coef for m in self._modules)
        return total / self.coef

    def calculate_credits(self):
        if not self._modules:
            return 0
        if self.calculate_average() >= 10:      # compensation dans l'UE
            return self.credit
        return sum(m.calculate_credits() for m in self._modules)

    def summary(self):
        lines = [
            f"Unit: {self.title} ({self.name})",
            f"Coefficient: {self.coef}, Credits: {self.credit}",
            f"Average: {self.calculate_average():.2f}",
            f"Credits earned: {self.calculate_credits()}",
            "Modules:"
        ]
        for m in self._modules:
            lines.append(f"  - {m.name}: {m.title} (Avg: {m.calculate_average():.2f})")
        return "\n".join(lines)

# ===== MAIN =====
if __name__ == "__main__":
    m1 = Module("MTI", "Methods & Technologies of Implementation",
                coef=3, credit=5, hours_tp=1.5)
    m2 = Module("AABD", "Database architecture and administration",
                coef=2, credit=4, hours_tp=1.5)

    u11 = Unit("UEM11", "UE Méthodologie", [m1, m2])

    m1.set_grade(tp=10, exam=12)
    m2.set_grade(tp=8, exam=6)

    print("Module average:", m1.name, m1.calculate_average())
    print("Module average:", m2.name, m2.calculate_average())
    print("Unit coef:", u11.coef, "| Unit credits total:", u11.credit)
    print("Unit average:", u11.calculate_average())
    print("Unit credits:", u11.calculate_credits())

    # Test find_module
    trouve = u11.find_module("AABD")
    print("find_module('AABD') ->", trouve.title if trouve else None)

    # Test 2 : si l'UE est validée par compensation
    m2.set_grade(tp=12, exam=12)
    print("--- Après avoir amélioré AABD (12 et 12) ---")
    print("Unit average:", u11.calculate_average())
    print("Unit credits:", u11.calculate_credits())