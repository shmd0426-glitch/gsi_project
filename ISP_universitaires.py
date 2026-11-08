from abc import ABC, abstractmethod

# Interfaces séparées (une seule capacité chacune)
class Teacher(ABC):
    @abstractmethod
    def teach(self): ...

class Researcher(ABC):
    @abstractmethod
    def do_research(self): ...

class Doctor(ABC):
    @abstractmethod
    def practice_medicine(self): ...

# 1) Enseignant-chercheur
class ProfessorResearcher(Teacher, Researcher):
    def teach(self):
        print("Le professeur enseigne.")
    def do_research(self):
        print("Le professeur fait de la recherche.")

# 2) Chercheur à plein temps (n'enseigne pas)
class FullTimeResearcher(Researcher):
    def do_research(self):
        print("Le chercheur fait de la recherche à plein temps.")

# 3) Professeur hospitalo-universitaire : médecine + enseignement + recherche
class HospitalProfessorResearcher(Teacher, Researcher, Doctor):
    def teach(self):
        print("Le PU-PH enseigne.")
    def do_research(self):
        print("Le PU-PH fait de la recherche.")
    def practice_medicine(self):
        print("Le PU-PH exerce la médecine.")

if __name__ == '__main__':
    ProfessorResearcher().teach()
    FullTimeResearcher().do_research()
    h = HospitalProfessorResearcher()
    h.practice_medicine(); h.teach(); h.do_research()