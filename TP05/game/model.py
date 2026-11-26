"""MODÈLE : toute la logique du jeu (aucun dessin, aucun clavier).

Jeu de plateforme à défilement horizontal (style Mario) :
le monde est long, le joueur avance, recule, saute et tire.
"""
import math
import random
from abc import ABC, abstractmethod

import pygame

WIDTH, HEIGHT = 800, 600          # taille de l'écran
GROUND_Y = HEIGHT - 90            # hauteur du sol
ACTIVE_RANGE = 620                # un monstre ne bouge que s'il est proche
MAX_MONSTERS = 40                 # limite de monstres vivants en même temps
GRAVITY, JUMP_SPEED, MAX_FALL = 0.55, -13.5, 14

NOIR, BLANC = (0, 0, 0), (255, 255, 255)
ROUGE, ORANGE, VIOLET = (230, 50, 50), (255, 150, 0), (170, 90, 220)
VERT, JAUNE, CYAN = (40, 200, 90), (255, 220, 0), (60, 220, 255)
GRIS, BLEU_CLAIR, ROSE = (140, 140, 150), (120, 180, 255), (255, 105, 180)


# ============================================================
#  Armes et projectiles
# ============================================================
class Weapon:
    def __init__(self, name, damage, cooldown, color, speed=9,
                 pellets=1, spread=0):
        self.name, self.damage, self.cooldown = name, damage, cooldown
        self.color, self.speed = color, speed
        self.pellets, self.spread = pellets, math.radians(spread)


PISTOLET = Weapon("Pistolet", 1, 12, JAUNE)
LASER = Weapon("Laser", 2, 25, CYAN, speed=14)
FUSIL = Weapon("Fusil", 1, 35, ORANGE, speed=8, pellets=5, spread=10)
ECRASEMENT = Weapon("Écrasement", 2, 0, BLANC)      # saut sur la tête d'un monstre

# Armes du monde fantastique
ETINCELLE = Weapon("Étincelle", 1, 12, VIOLET)
BOULE_FEU = Weapon("Boule de feu", 2, 25, ORANGE, speed=11)
ARC = Weapon("Arc enchanté", 1, 32, VERT, speed=10, pellets=3, spread=12)

# Armes du monde spatial
BLASTER = Weapon("Blaster", 1, 10, CYAN, speed=11)
PLASMA = Weapon("Plasma", 3, 35, ROSE, speed=12)
RAFALE = Weapon("Rafale", 1, 30, BLANC, speed=10, pellets=5, spread=8)


class Bullet:
    def __init__(self, x, y, tx, ty, weapon=None, damage=1, color=JAUNE,
                 speed=9, angle_offset=0.0):
        angle = math.atan2(ty - y, tx - x) + angle_offset
        self.x, self.y = float(x), float(y)
        self.speed, self.direction = speed, angle      # vitesse et direction (énoncé)
        self.vx, self.vy = math.cos(angle) * speed, math.sin(angle) * speed
        self.weapon, self.damage, self.color = weapon, damage, color

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def get_rect(self):
        return pygame.Rect(int(self.x) - 4, int(self.y) - 4, 8, 8)

    def is_out(self, area):
        return not area.colliderect(self.get_rect())


class EnemyBullet(Bullet):
    def __init__(self, x, y, tx, ty):
        super().__init__(x, y, tx, ty, None, 10, ROUGE, speed=5)


# ============================================================
#  DIP : calcul des dégâts (abstraction injectée dans le monstre)
# ============================================================
class DamageCalculator(ABC):
    @abstractmethod
    def compute(self, weapon):
        ...


class NormalDamage(DamageCalculator):
    def compute(self, weapon):
        return weapon.damage


class ResistantDamage(DamageCalculator):
    def __init__(self, resistant_to, factor=0.5):
        self.resistant_to, self.factor = resistant_to, factor

    def compute(self, weapon):
        return weapon.damage * (self.factor if weapon.name in self.resistant_to else 1)


class WeaknessDamage(DamageCalculator):
    def __init__(self, weak_to, factor=2):
        self.weak_to, self.factor = weak_to, factor

    def compute(self, weapon):
        return weapon.damage * (self.factor if weapon.name in self.weak_to else 1)


# ============================================================
#  Monstres (LSP : même contrat pour tous)
#  update(target_rect) -> liste de projectiles
#  take_damage(weapon) -> True si détruit
# ============================================================
class Monster(ABC):
    SIZE, COLOR, SPEED, HP, POINTS = 32, ROUGE, 2, 1, 10
    CONTACT_DAMAGE = 20
    DROP_MULT = 1.0
    FLYING = False
    ATTACK_TYPE = "melee"        # type d'attaque : melee / flying / ranged / shield
    SPRITE = "blob"              # aspect pour la vue : blob / zombie / dragon / robot

    def __init__(self, x, y, damage_calculator=None):
        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE)
        self.fx, self.fy = float(x), float(y)
        self.speed = float(self.SPEED)
        self.hp = self.max_hp = float(self.HP)
        self.points, self.color = self.POINTS, self.COLOR
        self.shield_up = False
        self.facing = -1
        self.attack_type = self.ATTACK_TYPE
        self.damage_calculator = damage_calculator or NormalDamage()

    def apply_difficulty(self, hp_factor, speed_factor):
        self.hp *= hp_factor
        self.max_hp = self.hp
        self.speed *= speed_factor

    def take_damage(self, weapon):
        self.hp -= self.damage_calculator.compute(weapon)
        return self.hp <= 0

    def _walk_towards(self, target, speed):
        """Marche sur le sol vers le joueur (déplacement horizontal)."""
        dx = target.centerx - self.rect.centerx
        if abs(dx) > 2:
            self.facing = 1 if dx > 0 else -1
            self.fx += self.facing * speed
        self.rect.x = round(self.fx)

    def _step_towards(self, target, speed, wave=0.0):
        """Vole vers le joueur (déplacement 2D)."""
        dx, dy = target.centerx - self.rect.centerx, target.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            ux, uy = dx / dist, dy / dist
            self.fx += ux * speed - uy * wave
            self.fy += uy * speed + ux * wave
            self.rect.x, self.rect.y = round(self.fx), round(self.fy)
        if dx:
            self.facing = 1 if dx > 0 else -1

    @abstractmethod
    def update(self, target_rect):
        ...


class NormalMonster(Monster):
    def update(self, target_rect):
        self._walk_towards(target_rect, self.speed)
        return []


class FastMonster(NormalMonster):
    SIZE, COLOR, SPEED, POINTS, CONTACT_DAMAGE = 24, ORANGE, 4, 20, 15


class StrongMonster(NormalMonster):
    """Gros, lent, 4 PV, résistant au pistolet."""
    SIZE, COLOR, SPEED, HP, POINTS = 48, VIOLET, 1, 4, 30
    CONTACT_DAMAGE, DROP_MULT = 30, 1.5

    def __init__(self, x, y):
        super().__init__(x, y, ResistantDamage({"Pistolet"}, 0.5))


class FlyingMonster(Monster):
    """Vole en zigzag, faible contre le laser."""
    ATTACK_TYPE = "flying"
    SIZE, COLOR, SPEED, HP, POINTS, FLYING = 30, BLEU_CLAIR, 2.5, 2, 25, True

    def __init__(self, x, y):
        super().__init__(x, y, WeaknessDamage({"Laser"}, 2))
        self.t = random.random() * 6

    def update(self, target_rect):
        self.t += 0.12
        self._step_towards(target_rect, self.speed, wave=math.sin(self.t) * 3)
        return []


class ImmobileMonster(Monster):
    """Tourelle : ne bouge pas, tire sur le joueur."""
    ATTACK_TYPE = "ranged"
    SIZE, COLOR, HP, POINTS, DROP_MULT = 40, GRIS, 3, 30, 1.5

    def __init__(self, x, y):
        super().__init__(x, y)
        self.cooldown = random.randint(30, 90)

    def update(self, target_rect):
        self.facing = 1 if target_rect.centerx > self.rect.centerx else -1
        self.cooldown -= 1
        if self.cooldown <= 0:
            self.cooldown = 100
            return [EnemyBullet(*self.rect.center, *target_rect.center)]
        return []


class ShieldedMonster(Monster):
    """Avance et active périodiquement un bouclier (invulnérable)."""
    ATTACK_TYPE = "shield"
    SIZE, COLOR, SPEED, HP, POINTS, DROP_MULT = 36, VERT, 1.5, 3, 40, 1.5

    def __init__(self, x, y):
        super().__init__(x, y)
        self.timer = random.randint(0, 100)

    def take_damage(self, weapon):
        return False if self.shield_up else super().take_damage(weapon)

    def update(self, target_rect):
        self.timer += 1
        self.shield_up = (self.timer % 180) < 80
        self._walk_towards(target_rect, self.speed)
        return []


# ============================================================
#  Nouveaux monstres du TP5 : Zombie, Dragon, Robot
# ============================================================
class FireBall(Bullet):
    """Boule de feu du dragon."""
    def __init__(self, x, y, tx, ty):
        super().__init__(x, y, tx, ty, None, 15, ORANGE, speed=4.5)


class LaserShot(Bullet):
    """Tir du robot."""
    def __init__(self, x, y, tx, ty):
        super().__init__(x, y, tx, ty, None, 12, CYAN, speed=6.5)


class Zombie(NormalMonster):
    """Lent, 3 PV, faible contre le feu. Il se relève une fois après sa mort."""
    SPRITE = "zombie"
    SIZE, COLOR, SPEED, HP, POINTS = 38, (110, 150, 90), 1.2, 3, 30
    CONTACT_DAMAGE, DROP_MULT = 25, 1.3

    def __init__(self, x, y):
        super().__init__(x, y, WeaknessDamage({"Boule de feu"}, 2))
        self.revived = False

    def take_damage(self, weapon):
        dead = super().take_damage(weapon)
        if dead and not self.revived:          # première mort : il se relève
            self.revived = True
            self.hp = self.max_hp / 2
            return False
        return dead


class Dragon(Monster):
    """Vole au-dessus du joueur et crache des boules de feu (résiste au feu)."""
    ATTACK_TYPE, SPRITE = "flying", "dragon"
    SIZE, COLOR, SPEED, HP, POINTS, FLYING = 44, (215, 85, 45), 1.6, 4, 45, True
    CONTACT_DAMAGE, DROP_MULT = 25, 2.0

    def __init__(self, x, y):
        super().__init__(x, y, ResistantDamage({"Boule de feu"}, 0.5))
        self.t = random.random() * 6
        self.cooldown = random.randint(60, 120)

    def update(self, target_rect):
        self.t += 0.06
        above = target_rect.move(0, -140)            # il plane au-dessus du joueur
        if math.hypot(above.centerx - self.rect.centerx,
                      above.centery - self.rect.centery) > 12:
            self._step_towards(above, self.speed, wave=math.sin(self.t) * 1.5)
        self.facing = 1 if target_rect.centerx > self.rect.centerx else -1
        self.cooldown -= 1
        if self.cooldown <= 0:
            self.cooldown = 140
            return [FireBall(*self.rect.center, *target_rect.center)]
        return []


class Robot(Monster):
    """Avance puis s'arrête à distance et tire (résiste au Blaster)."""
    ATTACK_TYPE, SPRITE = "ranged", "robot"
    SIZE, COLOR, SPEED, HP, POINTS = 40, (150, 165, 190), 1.6, 4, 40
    CONTACT_DAMAGE, DROP_MULT = 20, 1.5

    def __init__(self, x, y):
        super().__init__(x, y, ResistantDamage({"Blaster"}, 0.5))
        self.cooldown = random.randint(40, 100)

    def update(self, target_rect):
        dx = abs(target_rect.centerx - self.rect.centerx)
        if dx > 300:
            self._walk_towards(target_rect, self.speed)
        else:
            self.facing = 1 if target_rect.centerx > self.rect.centerx else -1
        self.cooldown -= 1
        if self.cooldown <= 0 and dx < 520:
            self.cooldown = 90
            return [LaserShot(*self.rect.center, *target_rect.center)]
        return []


# ============================================================
#  Rewards : chacun sait s'appliquer au joueur
# ============================================================
class Reward(ABC):
    SIZE, LABEL, COLOR, LIFETIME = 22, "?", JAUNE, 600

    def __init__(self, x, y, value):
        self.rect = pygame.Rect(int(x - self.SIZE / 2), int(y - self.SIZE / 2),
                                self.SIZE, self.SIZE)
        self.type = type(self).__name__
        self.value = value
        self.timer = self.LIFETIME
        self.falls, self.vy = True, 0.0      # False = flotte (récompense posée)

    @abstractmethod
    def apply(self, player):
        """Applique l'effet, retourne le message à afficher."""


class HealthReward(Reward):
    LABEL, COLOR = "+", ROSE

    def apply(self, player):
        player.heal(self.value)
        return f"+{self.value} PV"


class ScoreReward(Reward):
    LABEL, COLOR = "$", JAUNE

    def apply(self, player):
        player.score += self.value
        return f"+{self.value} pts"


class WeaponReward(Reward):
    LABEL, COLOR = "W", ORANGE

    def apply(self, player):
        if player.unlock_weapon(self.value):
            return f"Arme : {self.value.name} !"
        player.score += 50
        return "+50 pts"


class SpeedReward(Reward):
    LABEL, COLOR = "S", VERT

    def apply(self, player):
        player.effects["speed"] = self.value
        return "Vitesse !"


class ShieldReward(Reward):
    LABEL, COLOR = "B", CYAN

    def apply(self, player):
        player.effects["shield"] = self.value
        return "Bouclier !"


# Variantes de rewards propres à chaque monde (même effet, autre aspect)
class PotionReward(HealthReward):          # monde fantastique
    LABEL = "P"


class GemReward(ScoreReward):              # monde fantastique
    LABEL, COLOR = "G", BLEU_CLAIR


class EnergyCellReward(HealthReward):      # monde spatial
    LABEL = "E"


class CrystalReward(ScoreReward):          # monde spatial
    LABEL, COLOR = "C", VIOLET


def placed_reward(cls, x, y, value):
    """Reward posé dans le niveau : il flotte et ne disparaît jamais."""
    reward = cls(x, y, value)
    reward.falls, reward.timer = False, 10 ** 9
    return reward


# ============================================================
#  PATTERN 1 - FACTORY METHOD : création des monstres
#  Chaque fabrique concrète redéfinit create_monster().
#  spawn() est commun : placement + difficulté.
# ============================================================
class MonsterFactory(ABC):
    MONSTER_CLASS = Monster          # sert à connaître la taille et le vol

    @abstractmethod
    def create_monster(self, x, y):
        """Méthode de fabrication (Factory Method)."""

    def spawn(self, x, hp_factor=1.0, speed_factor=1.0, rng=random):
        cls = self.MONSTER_CLASS
        y = rng.randint(120, GROUND_Y - 140) if cls.FLYING else GROUND_Y - cls.SIZE
        monster = self.create_monster(x, y)
        monster.apply_difficulty(hp_factor, speed_factor)
        return monster


class NormalMonsterFactory(MonsterFactory):
    MONSTER_CLASS = NormalMonster
    def create_monster(self, x, y): return NormalMonster(x, y)


class FastMonsterFactory(MonsterFactory):
    MONSTER_CLASS = FastMonster
    def create_monster(self, x, y): return FastMonster(x, y)


class StrongMonsterFactory(MonsterFactory):
    MONSTER_CLASS = StrongMonster
    def create_monster(self, x, y): return StrongMonster(x, y)


class FlyingMonsterFactory(MonsterFactory):
    MONSTER_CLASS = FlyingMonster
    def create_monster(self, x, y): return FlyingMonster(x, y)


class ImmobileMonsterFactory(MonsterFactory):
    MONSTER_CLASS = ImmobileMonster
    def create_monster(self, x, y): return ImmobileMonster(x, y)


class ShieldedMonsterFactory(MonsterFactory):
    MONSTER_CLASS = ShieldedMonster
    def create_monster(self, x, y): return ShieldedMonster(x, y)


class ZombieFactory(MonsterFactory):
    MONSTER_CLASS = Zombie
    def create_monster(self, x, y): return Zombie(x, y)


class DragonFactory(MonsterFactory):
    MONSTER_CLASS = Dragon
    def create_monster(self, x, y): return Dragon(x, y)


class RobotFactory(MonsterFactory):
    MONSTER_CLASS = Robot
    def create_monster(self, x, y): return Robot(x, y)


# ============================================================
#  PATTERN 2 - ABSTRACT FACTORY : les mondes
#  Un monde = une famille compatible : décor, monstres, armes, rewards.
# ============================================================
class WorldFactory(ABC):
    NAME, THEME = "", ""             # nom du monde et décor associé
    BONUS_WEAPON = None              # arme à trouver dans le niveau
    HEALTH_REWARD, SCORE_REWARD = HealthReward, ScoreReward

    def __init__(self):
        self._monsters = self.monster_factories()

    # --- produits que chaque monde doit fournir ---
    @abstractmethod
    def monster_factories(self):
        """dict : nom du monstre -> MonsterFactory."""

    @abstractmethod
    def create_weapons(self):
        """Armes de départ du joueur dans ce monde."""

    # --- opérations communes ---
    def monster_kinds(self):
        return list(self._monsters)

    def create_monster(self, kind, x, hp_factor=1.0, speed_factor=1.0, rng=random):
        if kind not in self._monsters:
            raise ValueError(f"Le monde « {self.NAME} » n'a pas de monstre « {kind} »")
        return self._monsters[kind].spawn(x, hp_factor, speed_factor, rng)

    def create_reward(self, kind, x, y):
        """Reward posé dans le niveau : "health", "score" ou "weapon"."""
        if kind == "health":
            return placed_reward(self.HEALTH_REWARD, x, y, 25)
        if kind == "score":
            return placed_reward(self.SCORE_REWARD, x, y, 20)
        if kind == "weapon":
            return placed_reward(WeaponReward, x, y, self.BONUS_WEAPON)
        raise ValueError("Reward inconnu : " + kind)

    def drop_table(self):
        """(classe, poids, valeur, condition) : butin des monstres vaincus."""
        bonus = self.BONUS_WEAPON
        return [
            (self.HEALTH_REWARD, 3, 25, lambda p: p.health < p.MAX_HEALTH),
            (self.SCORE_REWARD, 4, 50, lambda p: True),
            (SpeedReward, 2, 360, lambda p: True),
            (ShieldReward, 2, 300, lambda p: True),
            (WeaponReward, 1, bonus, lambda p: bonus is not None and bonus not in p.weapons),
        ]

    def random_drop(self, x, y, player):
        options = [(c, w, v) for c, w, v, ok in self.drop_table() if ok(player)]
        cls, _, value = random.choices(options, weights=[o[1] for o in options])[0]
        return cls(x, y, value)


class ClassicWorldFactory(WorldFactory):
    """Monde de la chambre : les monstres et armes du TP4."""
    NAME, THEME, BONUS_WEAPON = "Monde classique", "sunset", FUSIL

    def monster_factories(self):
        return {"normal": NormalMonsterFactory(), "fast": FastMonsterFactory(),
                "strong": StrongMonsterFactory(), "flying": FlyingMonsterFactory(),
                "immobile": ImmobileMonsterFactory(), "shielded": ShieldedMonsterFactory()}

    def create_weapons(self):
        return [PISTOLET, LASER]


class FantasyWorldFactory(WorldFactory):
    """Monde fantastique : zombies, dragons, sorts et potions."""
    NAME, THEME, BONUS_WEAPON = "Monde fantastique", "night", ARC
    HEALTH_REWARD, SCORE_REWARD = PotionReward, GemReward

    def monster_factories(self):
        return {"zombie": ZombieFactory(), "dragon": DragonFactory(),
                "fast": FastMonsterFactory(), "shielded": ShieldedMonsterFactory()}

    def create_weapons(self):
        return [ETINCELLE, BOULE_FEU]


class SpaceWorldFactory(WorldFactory):
    """Monde spatial : robots, drones, blasters et cellules d'énergie."""
    NAME, THEME, BONUS_WEAPON = "Monde spatial", "space", RAFALE
    HEALTH_REWARD, SCORE_REWARD = EnergyCellReward, CrystalReward

    def monster_factories(self):
        return {"robot": RobotFactory(), "flying": FlyingMonsterFactory(),
                "immobile": ImmobileMonsterFactory(), "strong": StrongMonsterFactory()}

    def create_weapons(self):
        return [BLASTER, PLASMA]


# ============================================================
#  PATTERN 3 - BUILDER : construction d'un niveau étape par étape
# ============================================================
class Level:
    """Produit : un niveau complet (décor, plateformes, monstres, rewards)."""
    def __init__(self):
        self.name, self.world, self.theme = "", None, ""
        self.length, self.flag_x = 0, 0
        self.platforms, self.monsters, self.rewards = [], [], []


class LevelBuilder(ABC):
    """Interface : les étapes de construction d'un niveau."""
    @abstractmethod
    def set_world(self, world, name): ...
    @abstractmethod
    def set_size(self, length): ...
    @abstractmethod
    def build_platforms(self, rng): ...
    @abstractmethod
    def place_monsters(self, config, rng): ...
    @abstractmethod
    def place_weapons(self): ...
    @abstractmethod
    def place_rewards(self): ...
    @abstractmethod
    def get_result(self): ...


class ConcreteLevelBuilder(LevelBuilder):
    def __init__(self):
        self.level = Level()
        self._taken = set()             # plateformes qui portent déjà un objet

    def set_world(self, world, name):
        """Choisit le monde : donne le décor (background) et la famille d'objets."""
        self.level.world, self.level.name = world, name
        self.level.theme = world.THEME

    def set_size(self, length):
        self.level.length = length
        self.level.flag_x = length - 150          # drapeau d'arrivée

    def build_platforms(self, rng):
        """Le sol (premier élément) + des plateformes flottantes."""
        length = self.level.length
        plats = [pygame.Rect(0, GROUND_Y, length, HEIGHT - GROUND_Y)]
        x = 450
        while x < length - 700:
            w, h = rng.choice([100, 140, 180]), rng.choice([95, 115, 135])
            plats.append(pygame.Rect(x, GROUND_Y - h, w, 22))
            if rng.random() < 0.3:                 # une marche pour monter plus haut
                plats.append(pygame.Rect(x + w + 70, GROUND_Y - h - 95, 110, 22))
            x += w + rng.randint(280, 520)
        self.level.platforms = plats

    def place_monsters(self, config, rng):
        """Répartit les monstres sur toute la longueur (via la fabrique du monde)."""
        kinds, weights = zip(*config.monster_types)
        span = self.level.length - 1500
        for i in range(config.monster_count):
            x = 750 + int(span * (i + 0.5) / config.monster_count) + rng.randint(-60, 60)
            kind = rng.choices(kinds, weights=weights)[0]
            self.level.monsters.append(self.level.world.create_monster(
                kind, x, config.hp_factor, config.speed_factor, rng))

    def place_weapons(self):
        """L'arme bonus du monde est posée sur la 2e plateforme."""
        plats, world = self.level.platforms[1:], self.level.world
        if len(plats) > 1 and world.BONUS_WEAPON is not None:
            p = plats[1]
            self._taken.add(1)
            self.level.rewards.append(world.create_reward("weapon", p.centerx, p.top - 22))

    def place_rewards(self):
        """Une pièce sur chaque plateforme libre, un soin au milieu du niveau."""
        plats, world = self.level.platforms[1:], self.level.world
        middle = min(plats, key=lambda p: abs(p.centerx - self.level.length / 2))
        for i, p in enumerate(plats):
            if i in self._taken:
                continue
            kind = "health" if p is middle else "score"
            self.level.rewards.append(world.create_reward(kind, p.centerx, p.top - 22))

    def get_result(self):
        return self.level


class LevelDirector:
    """Connaît l'ordre des étapes ; le builder sait les réaliser."""
    def build(self, builder, config):
        rng = random.Random(config.seed)           # même niveau à chaque partie
        builder.set_world(config.world, config.name)
        builder.set_size(config.length)
        builder.build_platforms(rng)
        builder.place_monsters(config, rng)
        builder.place_weapons()
        builder.place_rewards()
        return builder.get_result()


# ============================================================
#  OCP : les niveaux sont des données
# ============================================================
class LevelConfig:
    def __init__(self, name, length, monster_count, monster_types, world, seed,
                 hp_factor=1.0, speed_factor=1.0, reward_chance=0.3):
        unknown = [k for k, _ in monster_types if k not in world.monster_kinds()]
        if unknown:
            raise ValueError(f"{name} : monstres absents du monde {world.NAME} : {unknown}")
        self.name, self.length = name, length         # length = longueur du monde (px)
        self.monster_count = monster_count
        self.monster_types = monster_types            # liste de (nom, poids)
        self.world, self.seed = world, seed           # famille d'objets + graine
        self.hp_factor, self.speed_factor = hp_factor, speed_factor
        self.reward_chance = reward_chance

    @property
    def theme(self):                                   # le décor vient du monde
        return self.world.THEME


LEVELS = [
    LevelConfig("Le coucher", 4800, 10, [("normal", 1)],
                ClassicWorldFactory(), seed=1, reward_chance=0.35),
    LevelConfig("Minuit", 6400, 16,
                [("zombie", 3), ("fast", 2), ("dragon", 2), ("shielded", 1)],
                FantasyWorldFactory(), seed=2),
    LevelConfig("Au-delà des étoiles", 8000, 22,
                [("robot", 3), ("flying", 2), ("immobile", 2), ("strong", 2)],
                SpaceWorldFactory(), seed=3, hp_factor=1.2, speed_factor=1.15,
                reward_chance=0.25),
]


# ============================================================
#  Joueur : position, vitesse, santé, arme, score + physique Mario
# ============================================================
class Player:
    MAX_HEALTH = 100
    WIDTH, HEIGHT = 30, 50

    def __init__(self, x, y, weapons=None, score=0):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.px, self.py = float(x), float(y)
        self.vy, self.kb = 0.0, 0.0           # vitesse verticale, recul
        self.on_ground, self.jump_held = False, False
        self.facing, self.walk_phase, self.moving = 1, 0.0, False
        self.base_speed = 4.5
        self.health = float(self.MAX_HEALTH)
        self.score = score
        self.cooldown = self.invincible = 0
        self.weapons = list(weapons) if weapons else [PISTOLET, LASER]
        self.weapon_index = 0
        self.effects = {}                     # "speed"/"shield" -> frames

    @property
    def weapon(self):
        return self.weapons[self.weapon_index]

    @property
    def speed(self):
        return self.base_speed * (1.6 if "speed" in self.effects else 1)

    @property
    def shielded(self):
        return "shield" in self.effects

    def is_dead(self):
        return self.health <= 0

    def update_physics(self, dx, jump, support, world_width):
        """Marche, saut, gravité et atterrissage sur les plateformes."""
        self.moving = dx != 0 and self.on_ground
        if dx:
            self.facing = 1 if dx > 0 else -1
            self.walk_phase += 0.2
        self.px += dx * self.speed + self.kb
        self.kb = 0.0 if abs(self.kb) < 0.3 else self.kb * 0.85
        self.px = max(0.0, min(self.px, world_width - self.rect.w))

        jumped = False
        if jump and self.on_ground and not self.jump_held:
            self.vy = JUMP_SPEED
            self.on_ground = False
            jumped = True
        self.jump_held = jump
        if not jump and self.vy < -4:          # saut court si on relâche
            self.vy = -4

        prev_bottom = self.rect.bottom
        self.vy = min(self.vy + GRAVITY, MAX_FALL)
        self.py += self.vy
        self.rect.topleft = (round(self.px), round(self.py))
        self.on_ground = False
        if self.vy >= 0:
            top = support(self.rect, prev_bottom)
            if top is not None:
                self.rect.bottom = top
                self.py, self.vy = float(self.rect.y), 0.0
                self.on_ground = True
        return jumped

    def select_weapon(self, index):
        if 0 <= index < len(self.weapons):
            self.weapon_index = index

    def unlock_weapon(self, weapon):
        if weapon in self.weapons:
            return False
        self.weapons.append(weapon)
        self.weapon_index = len(self.weapons) - 1
        return True

    def hit(self, amount):
        """True si les dégâts sont réellement appliqués."""
        if self.invincible > 0 or self.shielded:
            return False
        self.health -= amount
        self.invincible = 60
        return True

    def heal(self, amount):
        self.health = min(self.MAX_HEALTH, self.health + amount)

    def tick(self):
        self.cooldown = max(0, self.cooldown - 1)
        self.invincible = max(0, self.invincible - 1)
        for name in list(self.effects):
            self.effects[name] -= 1
            if self.effects[name] <= 0:
                del self.effects[name]


# ============================================================
#  Plateau de jeu : monde, collisions, niveaux, score, caméra
#  Le contrôleur envoie des commandes, la vue lit l'état.
# ============================================================
class GameModel:
    def __init__(self, levels=None):
        self.levels = levels or LEVELS
        self.director = LevelDirector()
        self.high_score = 0
        self.new_game()

    # ---------- niveaux ----------
    def new_game(self):
        self.level_index = 0
        self.checkpoint = {"score": 0}
        self.load_level()

    def load_level(self):
        """Construit le niveau avec le Builder, puis place le joueur."""
        cfg = self.config = self.levels[self.level_index]
        level = self.level = self.director.build(ConcreteLevelBuilder(), cfg)
        self.world = level.world
        self.length, self.flag_x = level.length, level.flag_x
        self.platforms = level.platforms
        self.monsters, self.rewards = level.monsters, level.rewards
        # armes de départ = celles du monde du niveau
        self.player = Player(100, GROUND_Y - Player.HEIGHT,
                             self.world.create_weapons(), self.checkpoint["score"])
        self.bullets, self.enemy_bullets, self.messages = [], [], []
        self.sound_events = []
        self.kills = 0
        self.camera_x = 0.0
        self.input_dx, self.input_jump = 0, False

    def next_level(self):
        self.level_index += 1
        self.load_level()

    def is_last_level(self):
        return self.level_index == len(self.levels) - 1

    @property
    def level_won(self):
        return self.player.rect.right >= self.flag_x

    def finish_level(self):
        self.checkpoint = {"score": self.player.score}
        self.bullets.clear()
        self.enemy_bullets.clear()
        self.record_score()
        self._sound("win")

    def record_score(self):
        self.high_score = max(self.high_score, self.player.score)

    # ---------- monde ----------
    def _support_y(self, rect, prev_bottom):
        """Hauteur de la plateforme sur laquelle `rect` atterrit (sinon None)."""
        for p in self.platforms:
            if (rect.right > p.left + 4 and rect.left < p.right - 4
                    and prev_bottom <= p.top + 1 and rect.bottom >= p.top):
                return p.top
        return None

    @property
    def view_rect(self):
        """Zone visible (un peu élargie) : les projectiles sortis disparaissent."""
        return pygame.Rect(int(self.camera_x) - 80, -100, WIDTH + 160, HEIGHT + 200)

    # ---------- commandes ----------
    def set_input(self, dx, jump):
        self.input_dx, self.input_jump = dx, jump

    def select_weapon(self, index):
        self.player.select_weapon(index)

    def nearest_monster(self):
        """Monstre visible le plus proche (pour l'auto-visée)."""
        p, cam = self.player.rect, self.camera_x
        visible = [m for m in self.monsters
                   if cam - 40 < m.rect.centerx < cam + WIDTH + 40]
        return min(visible, default=None,
                   key=lambda m: math.hypot(m.rect.centerx - p.centerx,
                                            m.rect.centery - p.centery))

    def fire(self, target=None):
        """Tire vers target (x, y monde), sinon vers le monstre proche ou tout droit."""
        p = self.player
        if p.is_dead() or p.cooldown > 0:
            return False
        if target is None:
            nearest = self.nearest_monster()
            target = nearest.rect.center if nearest else (
                p.rect.centerx + p.facing * 200, p.rect.centery)
        if abs(target[0] - p.rect.centerx) > 10:
            p.facing = 1 if target[0] > p.rect.centerx else -1
        origin = (p.rect.centerx + p.facing * 14, p.rect.y + 24)
        w = p.weapon
        for i in range(w.pellets):
            offset = (i - (w.pellets - 1) / 2) * w.spread
            self.bullets.append(Bullet(*origin, *target, w, w.damage,
                                       w.color, w.speed, offset))
        p.cooldown = w.cooldown
        self._sound("shoot")
        return True

    def spawn_monster(self, kind=None):
        """Crée un monstre à la demande, devant le joueur (Factory Method).

        `kind` : "zombie", "dragon", "robot"... Sans argument, un type est
        tiré au hasard parmi ceux du niveau. Plusieurs types peuvent donc
        coexister dans la même partie."""
        if len(self.monsters) >= MAX_MONSTERS or self.player.is_dead():
            return None
        if kind is None:
            kinds, weights = zip(*self.config.monster_types)
            kind = random.choices(kinds, weights=weights)[0]
        x = min(self.player.rect.centerx + 520 + random.randint(-40, 80),
                self.length - 200)
        monster = self.world.create_monster(kind, x, self.config.hp_factor,
                                            self.config.speed_factor)
        self.monsters.append(monster)
        self._message(f"{type(monster).__name__} !", monster.rect.centerx,
                      monster.rect.y - 10, ROUGE, 60)
        self._sound("spawn")
        return monster

    # ---------- événements internes ----------
    def _sound(self, name):
        self.sound_events.append(name)

    def pop_sounds(self):
        """Retourne et vide la file des événements sonores en attente."""
        events, self.sound_events = self.sound_events, []
        return events

    def _message(self, text, x, y, color=BLANC, ttl=45):
        self.messages.append([text, x, y, color, ttl])

    def _kill_monster(self, monster):
        self.player.score += monster.points
        self.kills += 1
        self.monsters.remove(monster)
        self._message(f"+{monster.points}", *monster.rect.center, JAUNE)
        self._sound("kill")
        if random.random() < min(1.0, self.config.reward_chance * monster.DROP_MULT):
            self.rewards.append(self.world.random_drop(*monster.rect.center, self.player))

    def _hurt_player(self, damage, kb, vy=None):
        p = self.player
        if p.hit(damage):
            p.kb = kb
            if vy is not None:
                p.vy, p.on_ground = vy, False
            self._sound("lose" if p.is_dead() else "hurt")

    def _touch_monster(self, monster):
        """Contact : sauter sur la tête = écraser, sinon on est blessé (recul)."""
        p = self.player
        if p.vy > 1 and p.rect.bottom - monster.rect.top < 22:
            p.vy, p.on_ground = -9.0, False
            p.invincible = max(p.invincible, 15)
            self._sound("stomp")
            if monster.take_damage(ECRASEMENT):
                self._kill_monster(monster)
        else:
            kb = 9.0 if p.rect.centerx > monster.rect.centerx else -9.0
            self._hurt_player(monster.CONTACT_DAMAGE, kb, vy=-6.0)

    # ---------- boucle de mise à jour ----------
    def update(self):
        p = self.player
        p.tick()
        if p.update_physics(self.input_dx, self.input_jump, self._support_y, self.length):
            self._sound("jump")

        # Caméra : suit le joueur vers l'avant ET vers l'arrière
        target = p.rect.centerx - WIDTH * 0.4
        self.camera_x += (target - self.camera_x) * 0.15
        self.camera_x = max(0.0, min(self.camera_x, self.length - WIDTH))

        # Interaction : les monstres proches bougent / attaquent
        for monster in self.monsters:
            if abs(monster.rect.centerx - p.rect.centerx) <= ACTIVE_RANGE:
                self.enemy_bullets.extend(monster.update(p.rect))
                if monster.rect.bottom > GROUND_Y:         # jamais sous le sol
                    monster.rect.bottom = GROUND_Y
                    monster.fy = float(monster.rect.y)

        for monster in self.monsters[:]:                  # monstre <-> joueur
            if p.rect.colliderect(monster.rect):
                self._touch_monster(monster)

        view = self.view_rect
        for eb in self.enemy_bullets[:]:                  # tir ennemi -> joueur
            eb.update()
            if eb.is_out(view):
                self.enemy_bullets.remove(eb)
            elif eb.get_rect().colliderect(p.rect):
                self.enemy_bullets.remove(eb)
                self._hurt_player(eb.damage, -5.0 * p.facing)

        if p.is_dead():
            return

        for bullet in self.bullets[:]:                    # balle -> monstre
            bullet.update()
            if bullet.is_out(view):
                self.bullets.remove(bullet)
                continue
            for monster in self.monsters[:]:
                if bullet.get_rect().colliderect(monster.rect):
                    self.bullets.remove(bullet)
                    if monster.take_damage(bullet.weapon):
                        self._kill_monster(monster)
                    else:
                        self._sound("hit")
                    break

        for reward in self.rewards[:]:                    # rewards
            reward.timer -= 1
            if reward.falls:                              # tombe jusqu'au sol
                prev = reward.rect.bottom
                reward.vy = min(reward.vy + 0.5, 10)
                reward.rect.y += int(reward.vy)
                top = self._support_y(reward.rect, prev)
                if top is not None:
                    reward.rect.bottom, reward.vy = top, 0.0
            if reward.timer <= 0:
                self.rewards.remove(reward)
            elif p.rect.colliderect(reward.rect):
                self._message(reward.apply(p), *reward.rect.center, CYAN, 70)
                self.rewards.remove(reward)
                self._sound("pickup")

        for m in self.messages:                           # textes flottants
            m[2] -= 1
            m[4] -= 1
        self.messages = [m for m in self.messages if m[4] > 0]