from module import Module
from unit import Unit
from semester import Semester


def create_module(
    name,
    title,
    coef,
    credit,
    lecture=1.5,
    td=0,
    tp=0,
    teaching_mode="In-person",
    continuous=40,
    exam=60,
):
    return Module(
        name=name,
        title=title,
        coef=coef,
        credit=credit,
        hours_lecture=lecture,
        hours_td=td,
        hours_tp=tp,
        teaching_mode=teaching_mode,
        continous_percent=continuous,
        exam_percent=exam,
    )


def build_semester1():
    # UE11 - Fondamentales
    f111 = create_module("F111", "Réseaux des couches basses", 3, 6, lecture=1.5, td=1.5, tp=1.5)
    f112 = create_module("F112", "Algorithmique Avancée et Complexité", 2, 4, lecture=1.5, tp=1.5)
    ue11 = Unit("UE11", "UE Fondamentales - UE11", [f111, f112])

    # UE12 - Fondamentales
    f121 = create_module("F121", "Système d'exploitation", 2, 4, lecture=1.5, td=1.5, tp=1.5)
    f122 = create_module("F122", "Architectures Modernes des Systèmes Informatiques", 2, 4, lecture=1.5, tp=1.5)
    ue12 = Unit("UE12", "UE Fondamentales - UE12", [f121, f122])

    # UEM11 - Méthodologie
    m111 = create_module("M111", "Architecture et administration des bases de données", 2, 4, lecture=1.5, tp=1.5)
    m112 = create_module("M112", "Méthodes et Technologies d'Implémentation", 3, 5, lecture=1.5, tp=1.5)
    uem11 = Unit("UEM11", "UE Méthodologie", [m111, m112])

    # D11 - Découverte
    d111 = create_module("D111", "Systèmes de Communication Vocaux et Vidéos", 2, 2, lecture=1.5, tp=1.5)
    d11 = Unit("D11", "UE Découverte", [d111])

    # UET11 - Transversale
    t111 = create_module(
        "T111", "Cloud Computing", 1, 1,
        lecture=1.5, teaching_mode="Distance", continuous=0, exam=100
    )
    uet11 = Unit("UET11", "UE Transversale", [t111])

    return Semester("S1", "Semestre 1", [ue11, ue12, uem11, d11, uet11])


def build_semester2():
    # UE21 - Fondamentales
    f211 = create_module("F211", "Les Middlewares pour les systèmes répartis", 3, 6, lecture=1.5, td=1.5, tp=1.5)
    f212 = create_module("F212", "Modélisation et Architectures logicielles", 2, 4, lecture=1.5, tp=1.5)
    ue21 = Unit("UE21", "UE Fondamentales - UE21", [f211, f212])

    # UE22 - Fondamentales
    f221 = create_module("F221", "Réseaux de la couche IP", 3, 6, lecture=1.5, td=1.5, tp=1.5)
    f222 = create_module("F222", "Introduction au Machine Learning", 2, 4, lecture=1.5, tp=1.5)
    ue22 = Unit("UE22", "UE Fondamentales - UE22", [f221, f222])

    # UEM21 - Méthodologie
    m211 = create_module("M211", "Infographie", 2, 3, lecture=1.5, tp=1.5)
    m212 = create_module("M212", "Gestion de l'incertain", 2, 3, lecture=1.5, td=1.5)
    uem21 = Unit("UEM21", "UE Méthodologie", [m211, m212])

    # D21 - Découverte
    d211 = create_module("D211", "Internet of Things", 2, 3, lecture=1.5, tp=1.5)
    d21 = Unit("D21", "UE Découverte", [d211])

    # UET21 - Transversale
    t211 = create_module(
        "T211", "Cybercriminalité", 1, 1,
        lecture=1.5, teaching_mode="Distance", continuous=0, exam=100
    )
    uet21 = Unit("UET21", "UE Transversale", [t211])

    return Semester("S2", "Semestre 2", [ue21, ue22, uem21, d21, uet21])


# Alias avec majuscule au cas où
build_Semester1 = build_semester1
build_Semester2 = build_semester2

