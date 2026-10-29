from canvas import build_semester1, build_semester2

class Student:
    def __init__(self, matricule, name):
        self.matricule = matricule
        self.name = name
        self.semesters = {"S1": build_semester1(), "S2": build_semester2()}

    def set_grade(self, semester, code, tp=None, td=None, exam=None):
        module = self.semesters[semester].find_module(code)
        if module is None:
            raise KeyError(f"Module inconnu : {code}")
        module.set_grade(tp=tp, td=td, exam=exam)

    def semester_average(self, semester):
        return self.semesters[semester].calculate_average()

    def semester_credits(self, semester):
        return self.semesters[semester].calculate_credits()

    def year_average(self):
        return (self.semester_average("S1") + self.semester_average("S2")) / 2

    def year_credits(self):
        return self.semester_credits("S1") + self.semester_credits("S2")

    def report(self, semester):
        s = self.semesters[semester]
        print(f"--- {self.name} ({self.matricule}) : {s.title} ---")
        for u in s._units:
            print(f"{u.name}: moyenne {u.calculate_average():.2f} "
                  f"| crédits {u.calculate_credits()}/{u.credit}")
            for m in u._modules:
                print(f"    {m.name}: {m.calculate_average():.2f} "
                      f"({m.calculate_credits()}/{m.credit} crédits)")
        print(f"MOYENNE SEMESTRE : {s.calculate_average():.2f} "
              f"| CRÉDITS : {s.calculate_credits()}/{s.credit}")
from student import Student

if __name__ == "__main__":
    etu = Student("20240001", "Ahmed Benali")
    etu.set_grade("S1", "F111", tp=14, td=12, exam=11)
    etu.set_grade("S1", "F112", tp=10, exam=9)
    etu.set_grade("S1", "M112", tp=15, exam=13)
    etu.set_grade("S1", "T111", exam=16)
    # ... compléter pour les autres modules
    etu.report("S1")
    print("Crédits de l'année :", etu.year_credits(), "/ 60")