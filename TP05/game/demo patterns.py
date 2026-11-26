"""Démonstration en console des trois design patterns du TP5.

Lancer :  python demo_patterns.py
(aucune fenêtre : on affiche seulement ce que les patterns fabriquent)
"""
from collections import Counter

from model import (LEVELS, ClassicWorldFactory, ConcreteLevelBuilder,
                   DragonFactory, FantasyWorldFactory, LevelDirector,
                   RobotFactory, SpaceWorldFactory, ZombieFactory)


def titre(texte):
    print("\n" + "=" * 60 + f"\n{texte}\n" + "=" * 60)


# ------------------------------------------------------------------
titre("1) FACTORY METHOD : monstres créés à la demande")
for factory in (ZombieFactory(), DragonFactory(), RobotFactory()):
    m = factory.spawn(x=1000)
    print(f"{type(factory).__name__:<15} -> {type(m).__name__:<7} "
          f"PV={m.hp:g}  vitesse={m.speed:g}  vole={m.FLYING}  "
          f"attaque={m.attack_type}")

print("\nPlusieurs types dans la même partie :")
monstres = [f.spawn(x=1000 + 100 * i) for i, f in
            enumerate((ZombieFactory(), RobotFactory(), DragonFactory(), ZombieFactory()))]
print(Counter(type(m).__name__ for m in monstres))

# ------------------------------------------------------------------
titre("2) ABSTRACT FACTORY : un monde = une famille d'objets compatibles")
for world in (ClassicWorldFactory(), FantasyWorldFactory(), SpaceWorldFactory()):
    print(f"\n{world.NAME}")
    print("  décor           :", world.THEME)
    print("  monstres        :", ", ".join(world.monster_kinds()))
    print("  armes de départ :", ", ".join(w.name for w in world.create_weapons()))
    print("  arme bonus      :", world.BONUS_WEAPON.name)
    print("  reward soin     :", world.HEALTH_REWARD.__name__)
    print("  reward points   :", world.SCORE_REWARD.__name__)

print("\nUn monde refuse les monstres qui ne sont pas de sa famille :")
try:
    ClassicWorldFactory().create_monster("dragon", 1000)
except ValueError as erreur:
    print("  Erreur :", erreur)

# ------------------------------------------------------------------
titre("3) BUILDER : construction d'un niveau étape par étape")
director = LevelDirector()
for config in LEVELS:
    level = director.build(ConcreteLevelBuilder(), config)
    print(f"\nNiveau « {level.name} »")
    print("  monde      :", level.world.NAME)
    print("  décor      :", level.theme)
    print("  longueur   :", level.length, "px (drapeau en x =", level.flag_x, ")")
    print("  plateformes:", len(level.platforms) - 1)
    print("  monstres   :", dict(Counter(type(m).__name__ for m in level.monsters)))
    print("  rewards    :", dict(Counter(type(r).__name__ for r in level.rewards)))
    arme = next(r for r in level.rewards if r.type == "WeaponReward")
    print(f"  arme posée : {arme.value.name} en x = {arme.rect.centerx}")