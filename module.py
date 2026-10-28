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
        if continous_percent + exam_percent != 100:
            raise ValueError("continu + examen doit valoir 100 %")
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
        for key, value in (("tp", tp), ("td", td), ("exam", exam)):
            if value is not None:
                if not 0 <= value <= 20:
                    raise ValueError(f"Note {key} invalide : {value}")
                self._grades[key] = value

    def get_grade(self, key):
        return self._grades[key]

    def _weights(self):
        """Méthode privée : pondérations (tp, td, exam) en %."""
        cc = self.evaluation_continous_percent
        if self.hours_tp and self.hours_td:
            return cc / 2, cc / 2, self.evaluation_exam_percent
        if self.hours_td:
            return 0, cc, self.evaluation_exam_percent
        if self.hours_tp:
            return cc, 0, self.evaluation_exam_percent
        return 0, 0, self.evaluation_exam_percent

    def calculate_average(self):
        w_tp, w_td, w_exam = self._weights()
        g = self._grades
        return (g["tp"] * w_tp + g["td"] * w_td + g["exam"] * w_exam) / 100

    def calculate_credits(self):
        return self.credit if self.calculate_average() >= 10 else 0

    def summary(self):
        return (
            f"Module: {self.title} ({self.name})\n"
            f"Coefficient: {self.coef}, Credits: {self.credit}\n"
            f"Hours: total {self.total_hours}, {self.hours_lecture} Lecture, "
            f"{self.hours_td} TD, {self.hours_tp} TP\n"
            f"Teaching mode: {self.teaching_mode}, "
            f"Evaluation mode: Continous: {self.evaluation_continous_percent}% "
            f"Exam: {self.evaluation_exam_percent}%"
        )


# ===== MAIN =====
if __name__ == "__main__":
    m = Module("MTI", "Methods and Technologies of Implementation",
               coef=3, credit=5, hours_tp=1.5)

    # Test 1 : calcul normal (doit donner le même résultat qu'avant)
    m.set_grade(tp=10, exam=12)
    print("Moyenne :", m.calculate_average())
    print("Crédits :", m.calculate_credits())

    # Test 2 : note invalide (25 > 20) -> erreur attendue
    try:
        m.set_grade(tp=25)
    except ValueError as e:
        print("Test 2 OK :", e)

    # Test 3 : pourcentages invalides (50 + 60 = 110) -> erreur attendue
    try:
        Module("X", "Test", continous_percent=50, exam_percent=60)
    except ValueError as e:
        print("Test 3 OK :", e)