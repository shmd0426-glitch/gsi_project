# Partie 1 - Application gestion de stock (Factory Method)
from abc import ABC, abstractmethod


class Compte(ABC):
    @abstractmethod
    def stock(self): ...
    @abstractmethod
    def achat(self): ...
    @abstractmethod
    def commande(self): ...


class Gestionnaire(Compte):
    def stock(self): print("Gestionnaire : gerer le stock")
    def achat(self): print("Gestionnaire : effectuer un achat")
    def commande(self): print("Gestionnaire : passer une commande")
    def revenus(self): print("Gestionnaire : consulter les revenus totaux")


class Vendeur(Compte):
    def stock(self): print("Vendeur : consulter le stock")
    def achat(self): print("Vendeur : effectuer un achat")
    def commande(self): print("Vendeur : passer une commande")
    def vendre(self): print("Vendeur : vendre un produit")


class Visiteur(Compte):
    def stock(self): print("Visiteur : visualiser le stock")
    def achat(self): print("Visiteur : effectuer un achat")
    def commande(self): print("Visiteur : passer une commande")


class CompteFactory(ABC):
    @abstractmethod
    def createCompte(self, type): ...


class ConcreteCompteFactory(CompteFactory):
    def createCompte(self, type):
        comptes = {"gestionnaire": Gestionnaire,
                   "vendeur": Vendeur,
                   "visiteur": Visiteur}
        if type.lower() not in comptes:
            raise ValueError("Type de compte inconnu : " + type)
        return comptes[type.lower()]()


if __name__ == "__main__":
    factory = ConcreteCompteFactory()
    for t in ("gestionnaire", "vendeur", "visiteur"):
        print("---", t, "---")
        c = factory.createCompte(t)
        c.stock()
        c.achat()
        c.commande()
    # Extra : fonctions specifiques
    factory.createCompte("gestionnaire").revenus()
    factory.createCompte("vendeur").vendre()
