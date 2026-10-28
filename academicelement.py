from abc import ABC, abstractmethod


class AcademicElement(ABC):
    def __init__(self, name, title):
        self.name = name
        self.title = title
        self._WEEKS = 15
        self.coef = 0
        self.credit = 0
        self.hours_lecture = 0
        self.hours_td = 0
        self.hours_tp = 0

    @abstractmethod
    def calculate_average(self): ...

    @abstractmethod
    def calculate_credits(self): ...


class Module(AcademicElement):
    def __init__(self, name="", title="", coef=1, credit=1,
                 hours_lecture=1.5, hours_td=0, hours_tp=0,
                 teaching_mode="In-person",
                 continous_percent=40, exam_percent=60):
        super().__init__(name, title)
        self.coef = coef
        self.credit = credit
        self.hours_lecture = hours_lecture
        self.hours_td = hours_td
        self.hours_tp = hours_tp
        self.teaching_mode = teaching_mode
        self.evaluation_continous_percent = continous_percent
        self.evaluation_exam_percent = exam_percent
        self.total_hours = self._WEEKS * (hours_lecture + hours_td + hours_tp)
        self._grades = {"tp": 0, "td": 0, "exam": 0}

    def set_grade(self, tp=None, td=None, exam=None):
        if tp is not None:
            self._grades["tp"] = tp
        if td is not None:
            self._grades["td"] = td
        if exam is not None:
            self._grades["exam"] = exam

    def calculate_average(self):
        tp = self._grades["tp"]
        td = self._grades["td"]
        exam = self._grades["exam"]
        percent_exam = self.evaluation_exam_percent
        percent_tp = percent_td = 0
        if self.hours_tp and self.hours_td:
            percent_tp = percent_td = self.evaluation_continous_percent / 2
        elif self.hours_td:
            percent_td = self.evaluation_continous_percent
        elif self.hours_tp:
            percent_tp = self.evaluation_continous_percent
        return (tp * percent_tp / 100 +
                td * percent_td / 100 +
                exam * percent_exam / 100)

    def calculate_credits(self):
        if self.calculate_average() >= 10:
            return self.credit
        return 0


class Unit(AcademicElement):
    def __init__(self, name, title, modules=None):
        super().__init__(name, title)
        self._modules = []
        for m in (modules or []):
            self.add_module(m)

    def add_module(self, module):
        self._modules.append(module)
        self.coef += module.coef
        self.credit += module.credit

    def calculate_average(self):
        if not self._modules:
            return 0
        total = sum(m.calculate_average() * m.coef for m in self._modules)
        return total / self.coef

    def calculate_credits(self):
        if not self._modules:
            return 0
        if self.calculate_average() >= 10:
            return self.credit
        return sum(m.calculate_credits() for m in self._modules)


# ===== MAIN =====
if __name__ == "__main__":
    m1 = Module("MTI", "Methods & Technologies of Implementation",
                coef=3, credit=5, hours_tp=1.5,
                continous_percent=40, exam_percent=60)
    m1.set_grade(tp=10, exam=12)
    print("Module average:", m1.name, m1.calculate_average())

    m2 = Module("AABD", "Database architecture and administration",
                coef=2, credit=4, hours_tp=1.5,
                continous_percent=40, exam_percent=60)
    u11 = Unit("UEM11", "UE Méthodologie", [m1, m2])
    m2.set_grade(tp=8, exam=6)
    print("Module average:", m2.name, m2.calculate_average())
    print("Unit average:", u11.calculate_average())
    print("Unit credits:", u11.calculate_credits())