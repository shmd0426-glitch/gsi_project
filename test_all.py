from module import Module
from unit import Unit
from semester import Semester


def test_module():
    print("=== TEST MODULE ===")
    m = Module("MTI", "Methods and Technologies of Implementation",
               coef=3, credit=5, hours_tp=1.5)
    m.set_grade(tp=10, exam=12)
    print("Moyenne :", m.calculate_average())
    print("Crédits :", m.calculate_credits())

    try:
        m.set_grade(tp=25)
    except ValueError as e:
        print("Note invalide refusée :", e)
    print()


def test_unit():
    print("=== TEST UNIT ===")
    m1 = Module("MTI", "Methods and Technologies of Implementation",
                coef=3, credit=5, hours_tp=1.5)
    m2 = Module("AABD", "Database architecture and administration",
                coef=2, credit=4, hours_tp=1.5)
    m1.set_grade(tp=10, exam=12)
    m2.set_grade(tp=8, exam=6)

    u = Unit("UEM11", "UE Méthodologie", [m1, m2])
    print("Moyenne de l'UE :", u.calculate_average())
    print("Crédits de l'UE :", u.calculate_credits())
    print()


def test_semester():
    print("=== TEST SEMESTER ===")
    m1 = Module("MTI", "Methods and Technologies of Implementation",
                coef=3, credit=5, hours_tp=1.5)
    m2 = Module("AABD", "Database architecture and administration",
                coef=2, credit=4, hours_tp=1.5)
    m1.set_grade(tp=10, exam=12)
    m2.set_grade(tp=8, exam=6)
    u1 = Unit("UEM11", "UE Méthodologie", [m1, m2])

    m3 = Module("F111", "Réseaux des couches basses",
                coef=3, credit=6, hours_td=1.5, hours_tp=1.5)
    m4 = Module("F112", "Algorithmique Avancée et Complexité",
                coef=2, credit=4, hours_tp=1.5)
    m3.set_grade(tp=14, td=12, exam=11)
    m4.set_grade(tp=10, exam=9)
    u2 = Unit("UEF11", "UE Fondamentale", [m3, m4])

    s1 = Semester("S1", "Semestre 1")
    s1.add_unit(u1)
    s1.add_unit(u2)
    print(s1.summary())
    print()


# ===== MAIN =====
if __name__ == "__main__":
    test_module()
    test_unit()
    test_semester()