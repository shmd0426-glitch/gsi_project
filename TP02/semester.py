from academicelement import AcademicElement
from module import Module
from unit import Unit


class Semester(AcademicElement):
    """فصل دراسي يحتوي على عدة وحدات تعليمية."""

    def __init__(self, name, title, units=None):
        super().__init__(name, title)
        self._units = []
        for u in (units or []):
            self.add_unit(u)

    def add_unit(self, unit):
        """إضافة وحدة إلى الفصل الدراسي."""
        self._units.append(unit)
        self.coef += unit.coef
        self.credit += unit.credit

    def find_module(self, code):
        """Recherche d'un module par son code à travers les unités."""
        for unit in self._units:
            m = unit.find_module(code)
            if m is not None:
                return m
        return None

    def calculate_average(self):
        """حساب معدل الفصل باستعمال معاملات الوحدات."""
        if not self._units:
            return 0

        total_weighted = sum(
            unit.calculate_average() * unit.coef
            for unit in self._units
        )

        total_coef = sum(
            unit.coef for unit in self._units
        )

        if total_coef == 0:
            return 0

        return total_weighted / total_coef

    def calculate_credits(self):
        """حساب مجموع الأرصدة المكتسبة في الفصل."""
        return sum(
            unit.calculate_credits()
            for unit in self._units
        )

    def summary(self):
        """عرض معلومات الفصل الدراسي."""
        lines = [
            f"{self.title} ({self.name})",
            f"Average: {self.calculate_average():.2f}",
            f"Credits earned: {self.calculate_credits()}",
            "",
            "Units:",
        ]

        for unit in self._units:
            lines.append(
                f"  - {unit.name}: {unit.title} | "
                f"Average: {unit.calculate_average():.2f} | "
                f"Credits: {unit.calculate_credits()}"
            )

        return "\n".join(lines)


# ===== MAIN =====
if __name__ == "__main__":
    # --- UE 1 : Méthodologie ---
    m1 = Module("MTI", "Methods and Technologies of Implementation",
                coef=3, credit=5, hours_tp=1.5)
    m2 = Module("AABD", "Database architecture and administration",
                coef=2, credit=4, hours_tp=1.5)
    m1.set_grade(tp=10, exam=12)
    m2.set_grade(tp=8, exam=6)
    u1 = Unit("UEM11", "UE Méthodologie", [m1, m2])

    # --- UE 2 : Fondamentale ---
    m3 = Module("F111", "Réseaux des couches basses",
                coef=3, credit=6, hours_td=1.5, hours_tp=1.5)
    m4 = Module("F112", "Algorithmique Avancée et Complexité",
                coef=2, credit=4, hours_tp=1.5)
    m3.set_grade(tp=14, td=12, exam=11)
    m4.set_grade(tp=10, exam=9)
    u2 = Unit("UEF11", "UE Fondamentale", [m3, m4])

    # --- Semestre ---
    s1 = Semester("S1", "Semestre 1")
    s1.add_unit(u1)
    s1.add_unit(u2)

    print(s1.summary())
