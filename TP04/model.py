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


# (classe, poids, valeur, condition)
REWARD_TABLE = [
    (HealthReward, 3, 25, lambda p: p.health < p.MAX_HEALTH),
    (ScoreReward, 4, 50, lambda p: True),
    (SpeedReward, 2, 360, lambda p: True),
    (ShieldReward, 2, 300, lambda p: True),
    (WeaponReward, 1, FUSIL, lambda p: FUSIL not in p.weapons),
]


def create_reward(x, y, player):
    options = [(c, w, v) for c, w, v, ok in REWARD_TABLE if ok(player)]
    cls, _, value = random.choices(options, weights=[o[1] for o in options])[0]
    return cls(x, y, value)


def placed_reward(cls, x, y, value):
    """Reward posé dans le niveau : il flotte et ne disparaît jamais."""
    reward = cls(x, y, value)
    reward.falls, reward.timer = False, 10 ** 9
    return reward


# ============================================================
#  OCP : les niveaux sont des données
# ============================================================
class LevelConfig:
    def __init__(self, name, length, monster_count, monster_types,
                 theme, seed, hp_factor=1.0, speed_factor=1.0,
                 reward_chance=0.3):
        self.name, self.length = name, length         # length = longueur du monde (px)
        self.monster_count = monster_count
        self.monster_types = monster_types            # liste de (classe, poids)
        self.theme, self.seed = theme, seed           # décor + graine de génération
        self.hp_factor, self.speed_factor = hp_factor, speed_factor
        self.reward_chance = reward_chance


LEVELS = [
    LevelConfig("Le coucher", 4800, 10, [(NormalMonster, 1)],
                theme="sunset", seed=1, reward_chance=0.35),
    LevelConfig("Minuit", 6400, 16,
                [(NormalMonster, 3), (FastMonster, 2), (StrongMonster, 1),
                 (FlyingMonster, 2)], theme="night", seed=2),
    LevelConfig("Avant l'aube", 8000, 22,
                [(FastMonster, 2), (StrongMonster, 2), (FlyingMonster, 2),
                 (ImmobileMonster, 2), (ShieldedMonster, 2)],
                theme="dawn", seed=3, hp_factor=1.2, speed_factor=1.15,
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

        if jump and self.on_ground and not self.jump_held:
            self.vy = JUMP_SPEED
            self.on_ground = False
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
    def __init__(self):
        self.high_score = 0
        self.new_game()

    # ---------- niveaux ----------
    def new_game(self):
        self.level_index = 0
        self.checkpoint = {"score": 0, "weapons": [PISTOLET, LASER]}
        self.load_level()

    def load_level(self):
        cfg = self.config = LEVELS[self.level_index]
        rng = random.Random(cfg.seed)              # même niveau à chaque partie
        self.length = cfg.length
        self.flag_x = self.length - 150            # drapeau d'arrivée
        self.platforms = self._build_platforms(rng)
        self.player = Player(100, GROUND_Y - Player.HEIGHT,
                             self.checkpoint["weapons"], self.checkpoint["score"])
        self.monsters, self.bullets = [], []
        self.enemy_bullets, self.rewards, self.messages = [], [], []
        self.kills = 0
        self.camera_x = 0.0
        self.input_dx, self.input_jump = 0, False
        self._place_monsters(rng)
        self._place_rewards()

    def next_level(self):
        self.level_index += 1
        self.load_level()

    def is_last_level(self):
        return self.level_index == len(LEVELS) - 1

    @property
    def level_won(self):
        return self.player.rect.right >= self.flag_x

    def finish_level(self):
        self.checkpoint = {"score": self.player.score,
                           "weapons": list(self.player.weapons)}
        self.bullets.clear()
        self.enemy_bullets.clear()
        self.record_score()

    def record_score(self):
        self.high_score = max(self.high_score, self.player.score)

    # ---------- construction du monde ----------
    def _build_platforms(self, rng):
        """Le sol (premier élément) + des plateformes flottantes."""
        plats = [pygame.Rect(0, GROUND_Y, self.length, HEIGHT - GROUND_Y)]
        x = 450
        while x < self.length - 700:
            w, h = rng.choice([100, 140, 180]), rng.choice([95, 115, 135])
            plats.append(pygame.Rect(x, GROUND_Y - h, w, 22))
            if rng.random() < 0.3:                 # une marche pour monter plus haut
                plats.append(pygame.Rect(x + w + 70, GROUND_Y - h - 95, 110, 22))
            x += w + rng.randint(280, 520)
        return plats

    def _place_monsters(self, rng):
        cfg = self.config
        types, weights = zip(*cfg.monster_types)
        span = self.length - 1500
        for i in range(cfg.monster_count):
            x = 750 + int(span * (i + 0.5) / cfg.monster_count) + rng.randint(-60, 60)
            cls = rng.choices(types, weights=weights)[0]
            y = rng.randint(120, GROUND_Y - 140) if cls.FLYING else GROUND_Y - cls.SIZE
            monster = cls(x, y)
            monster.apply_difficulty(cfg.hp_factor, cfg.speed_factor)
            self.monsters.append(monster)

    def _place_rewards(self):
        """Une étoile sur chaque plateforme, un soin au milieu, une arme au début."""
        plats = self.platforms[1:]
        middle = min(plats, key=lambda p: abs(p.centerx - self.length / 2))
        for i, p in enumerate(plats):
            pos = (p.centerx, p.top - 22)
            if p is middle:
                self.rewards.append(placed_reward(HealthReward, *pos, 25))
            elif i == 1 and self.level_index == 0:
                self.rewards.append(placed_reward(WeaponReward, *pos, FUSIL))
            else:
                self.rewards.append(placed_reward(ScoreReward, *pos, 20))

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
        return True

    # ---------- événements internes ----------
    def _message(self, text, x, y, color=BLANC, ttl=45):
        self.messages.append([text, x, y, color, ttl])

    def _kill_monster(self, monster):
        self.player.score += monster.points
        self.kills += 1
        self.monsters.remove(monster)
        self._message(f"+{monster.points}", *monster.rect.center, JAUNE)
        if random.random() < min(1.0, self.config.reward_chance * monster.DROP_MULT):
            self.rewards.append(create_reward(*monster.rect.center, self.player))

    def _touch_monster(self, monster):
        """Contact : sauter sur la tête = écraser, sinon on est blessé (recul)."""
        p = self.player
        if p.vy > 1 and p.rect.bottom - monster.rect.top < 22:
            p.vy, p.on_ground = -9.0, False
            p.invincible = max(p.invincible, 15)
            if monster.take_damage(ECRASEMENT):
                self._kill_monster(monster)
        elif p.hit(monster.CONTACT_DAMAGE):
            p.kb = 9.0 if p.rect.centerx > monster.rect.centerx else -9.0
            p.vy, p.on_ground = -6.0, False

    # ---------- boucle de mise à jour ----------
    def update(self):
        p = self.player
        p.tick()
        p.update_physics(self.input_dx, self.input_jump, self._support_y, self.length)

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
                if p.hit(eb.damage):
                    p.kb = -5.0 * p.facing

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

        for m in self.messages:                           # textes flottants
            m[2] -= 1
            m[4] -= 1
        self.messages = [m for m in self.messages if m[4] > 0]