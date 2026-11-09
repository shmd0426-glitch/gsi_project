import math
import random
from abc import ABC, abstractmethod

import pygame

# ============================================================
#  Couleurs
# ============================================================
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
ROUGE = (230, 50, 50)
ORANGE = (255, 150, 0)
VIOLET = (170, 90, 220)
VERT = (40, 200, 90)
JAUNE = (255, 220, 0)
CYAN = (60, 220, 255)
GRIS = (140, 140, 150)
BLEU_CLAIR = (120, 180, 255)

# Couleurs de la poupée
PEAU = (255, 214, 170)
CHEVEUX = (110, 60, 30)
ROBE = (255, 105, 180)
ROSE_JOUE = (255, 150, 150)
CHAUSSURE = (150, 30, 60)


def spawn_on_edge(width, height, size):
    """Position aléatoire sur un bord de l'écran."""
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        return random.randint(0, width - size), 0
    if side == "bottom":
        return random.randint(0, width - size), height - size
    if side == "left":
        return 0, random.randint(0, height - size)
    return width - size, random.randint(0, height - size)


# ============================================================
#  DIP : armes + abstraction du calcul des dégâts
#  Le monstre dépend de DamageCalculator (abstraction),
#  jamais d'une arme précise ni d'une formule précise.
# ============================================================
class Weapon:
    def __init__(self, name, damage, cooldown, color):
        self.name = name
        self.damage = damage
        self.cooldown = cooldown
        self.color = color


PISTOLET = Weapon("Pistolet", 1, 12, JAUNE)
LASER = Weapon("Laser", 2, 25, CYAN)


class DamageCalculator(ABC):
    @abstractmethod
    def compute(self, weapon):
        """Retourne les dégâts réellement subis avec cette arme."""


class NormalDamage(DamageCalculator):
    def compute(self, weapon):
        return weapon.damage


class ResistantDamage(DamageCalculator):
    """Résistant à certaines armes : dégâts réduits."""

    def __init__(self, resistant_to, factor=0.5):
        self.resistant_to = resistant_to
        self.factor = factor

    def compute(self, weapon):
        if weapon.name in self.resistant_to:
            return weapon.damage * self.factor
        return weapon.damage


class WeaknessDamage(DamageCalculator):
    """Faible contre certaines armes : dégâts supplémentaires."""

    def __init__(self, weak_to, factor=2):
        self.weak_to = weak_to
        self.factor = factor

    def compute(self, weapon):
        if weapon.name in self.weak_to:
            return weapon.damage * self.factor
        return weapon.damage


# ============================================================
#  ISP : capacités séparées (un monstre n'implémente que les siennes)
# ============================================================
class Movable(ABC):
    @abstractmethod
    def move(self, target_rect):
        """Se déplace vers la cible."""


class Shooter(ABC):
    @abstractmethod
    def shoot(self, target_rect):
        """Retourne la liste des projectiles tirés."""


class Flyer(ABC):
    @abstractmethod
    def fly(self, target_rect):
        """Se déplace en volant vers la cible."""


class Shielded(ABC):
    @abstractmethod
    def use_shield(self):
        """Met à jour l'état du bouclier."""


# ============================================================
#  Projectiles
# ============================================================
class Bullet:
    def __init__(self, x, y, target_x, target_y, weapon, speed=9):
        dx, dy = target_x - x, target_y - y
        distance = math.hypot(dx, dy) or 1
        self.x, self.y = float(x), float(y)
        self.vx = dx / distance * speed
        self.vy = dy / distance * speed
        self.weapon = weapon
        self.color = weapon.color

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def get_rect(self):
        return pygame.Rect(int(self.x) - 4, int(self.y) - 4, 8, 8)

    def is_out(self, screen_rect):
        return not screen_rect.colliderect(self.get_rect())

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 4)


class EnemyBullet(Bullet):
    """Projectile tiré par un monstre : touche le joueur."""

    def __init__(self, x, y, target_x, target_y):
        super().__init__(x, y, target_x, target_y,
                         Weapon("Boule", 1, 0, ROUGE), speed=5)


# ============================================================
#  Monstres
#  SRP : un monstre ne gère que ses données, sa vie et son
#        comportement. L'affichage est dans des classes séparées.
#  LSP : tous les monstres respectent le même contrat :
#        update(target_rect) -> liste de projectiles
#        take_damage(weapon) -> True si détruit
# ============================================================
class Monster(ABC):
    SIZE = 32
    COLOR = ROUGE
    SPEED = 2
    HP = 1
    POINTS = 10

    def __init__(self, width, height, damage_calculator=None):
        x, y = spawn_on_edge(width, height, self.SIZE)
        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE)
        self.fx, self.fy = float(x), float(y)
        self.speed = self.SPEED
        self.hp = float(self.HP)
        self.max_hp = float(self.HP)
        self.points = self.POINTS
        self.color = self.COLOR
        # DIP : dépend de l'abstraction, injectée de l'extérieur
        self.damage_calculator = damage_calculator or NormalDamage()

    def take_damage(self, weapon):
        """Retourne True si le monstre est détruit."""
        self.hp -= self.damage_calculator.compute(weapon)
        return self.hp <= 0

    def _step_towards(self, target_rect, speed, wave=0.0):
        dx = target_rect.centerx - self.rect.centerx
        dy = target_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            ux, uy = dx / dist, dy / dist
            self.fx += ux * speed - uy * wave
            self.fy += uy * speed + ux * wave
            self.rect.x = round(self.fx)
            self.rect.y = round(self.fy)

    @abstractmethod
    def update(self, target_rect):
        """Un tour de jeu. Retourne la liste des projectiles créés."""


class NormalMonster(Monster, Movable):
    """Monstre de base : marche vers le joueur."""

    def move(self, target_rect):
        self._step_towards(target_rect, self.speed)

    def update(self, target_rect):
        self.move(target_rect)
        return []


# --- OCP : nouveaux types ajoutés sans toucher à Monster ---
class FastMonster(NormalMonster):
    SIZE = 24
    COLOR = ORANGE
    SPEED = 4
    POINTS = 20


class StrongMonster(NormalMonster):
    """Gros, lent, 4 PV, résistant au pistolet."""
    SIZE = 48
    COLOR = VIOLET
    SPEED = 1
    HP = 4
    POINTS = 30

    def __init__(self, width, height):
        super().__init__(width, height, ResistantDamage({"Pistolet"}, 0.5))


class FlyingMonster(Monster, Flyer):
    """Vole en zigzag vers le joueur, faible contre le laser."""
    SIZE = 30
    COLOR = BLEU_CLAIR
    SPEED = 2.5
    HP = 2
    POINTS = 25

    def __init__(self, width, height):
        super().__init__(width, height, WeaknessDamage({"Laser"}, 2))
        self.t = random.random() * 6

    def fly(self, target_rect):
        self.t += 0.12
        self._step_towards(target_rect, self.speed, wave=math.sin(self.t) * 3)

    def update(self, target_rect):
        self.fly(target_rect)
        return []


class ImmobileMonster(Monster, Shooter):
    """Tourelle : ne bouge pas (pas de move()), mais tire sur le joueur."""
    SIZE = 40
    COLOR = GRIS
    HP = 3
    POINTS = 30

    def __init__(self, width, height):
        super().__init__(width, height)
        self.cooldown = random.randint(30, 90)

    def shoot(self, target_rect):
        return [EnemyBullet(self.rect.centerx, self.rect.centery,
                            target_rect.centerx, target_rect.centery)]

    def update(self, target_rect):
        self.cooldown -= 1
        if self.cooldown <= 0:
            self.cooldown = 100
            return self.shoot(target_rect)
        return []


class ShieldedMonster(Monster, Movable, Shielded):
    """Avance et active périodiquement un bouclier (invulnérable)."""
    SIZE = 36
    COLOR = VERT
    SPEED = 1.5
    HP = 3
    POINTS = 40

    def __init__(self, width, height):
        super().__init__(width, height)
        self.shield_up = False
        self.timer = random.randint(0, 100)

    def use_shield(self):
        self.timer += 1
        self.shield_up = (self.timer % 180) < 80

    def move(self, target_rect):
        self._step_towards(target_rect, self.speed)

    def take_damage(self, weapon):
        if self.shield_up:
            return False          # bouclier : aucun dégât
        return super().take_damage(weapon)

    def update(self, target_rect):
        self.use_shield()
        self.move(target_rect)
        return []


# ============================================================
#  OCP : les niveaux sont des DONNÉES.
#  Pour ajouter un niveau ou un monstre dans un niveau, on modifie
#  seulement cette liste : aucune classe existante n'est touchée.
# ============================================================
class LevelConfig:
    def __init__(self, name, target_kills, start_monsters, monster_types):
        self.name = name
        self.target_kills = target_kills        # monstres à détruire pour gagner
        self.start_monsters = start_monsters    # monstres présents au début
        self.monster_types = monster_types      # types qui peuvent apparaître


LEVELS = [
    LevelConfig("Échauffement", 8, 2,
                [NormalMonster]),
    LevelConfig("Ça se complique", 12, 3,
                [NormalMonster, FastMonster, StrongMonster, FlyingMonster]),
    LevelConfig("Le grand final", 15, 3,
                [FastMonster, StrongMonster, FlyingMonster,
                 ImmobileMonster, ShieldedMonster]),
]


# ============================================================
#  SRP : l'affichage est séparé du monstre
# ============================================================
class MonsterRenderer:
    def draw(self, screen, monster):
        r = monster.rect
        color = monster.color

        # Ailes si le monstre peut voler
        if isinstance(monster, Flyer):
            wing = pygame.Rect(0, 0, r.w // 2, r.h // 3)
            wing.midright = (r.x + 2, r.y + r.h // 3)
            pygame.draw.ellipse(screen, BLANC, wing)
            wing.midleft = (r.right - 2, r.y + r.h // 3)
            pygame.draw.ellipse(screen, BLANC, wing)

        # Corps arrondi
        body = pygame.Rect(r.x, r.y, r.w, int(r.h * 0.8))
        pygame.draw.rect(screen, color, body, border_radius=r.w // 3)

        # Petits pieds
        foot_w = max(4, r.w // 4)
        foot_y = r.y + int(r.h * 0.7)
        foot_h = r.h - int(r.h * 0.7)
        for i in range(3):
            fx = r.x + i * (r.w - foot_w) // 2
            pygame.draw.rect(screen, color, (fx, foot_y, foot_w, foot_h))

        # Yeux
        eye_y = r.y + r.h // 3
        eye_r = max(3, r.w // 6)
        for ex in (r.x + r.w // 3, r.x + 2 * r.w // 3):
            pygame.draw.circle(screen, BLANC, (ex, eye_y), eye_r)
            pygame.draw.circle(screen, NOIR, (ex, eye_y), max(1, eye_r // 2))

        # Bouclier actif
        if isinstance(monster, Shielded) and monster.shield_up:
            pygame.draw.circle(screen, CYAN, r.center, r.w // 2 + 6, 3)


class HealthBarRenderer:
    """Composant responsable uniquement de la barre de vie."""

    def draw(self, screen, monster):
        r = monster.rect
        ratio = max(0.0, monster.hp) / monster.max_hp
        pygame.draw.rect(screen, ROUGE, (r.x, r.y - 8, r.width, 4))
        pygame.draw.rect(screen, VERT, (r.x, r.y - 8, r.width * ratio, 4))


# ============================================================
#  Joueur
# ============================================================
class Player:
    """Petite poupée : couettes, robe rose, yeux qui suivent la cible."""

    def __init__(self):
        self.rect = pygame.Rect(386, 500, 28, 40)
        self.speed = 5
        self.lives = 3
        self.cooldown = 0
        self.invincible = 0
        self.weapons = [PISTOLET, LASER]
        self.weapon = PISTOLET

    def select_weapon(self, index):
        if 0 <= index < len(self.weapons):
            self.weapon = self.weapons[index]

    def update(self, screen_rect, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed
        self.rect.clamp_ip(screen_rect)
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.invincible > 0:
            self.invincible -= 1

    def can_shoot(self):
        return self.cooldown == 0

    def shoot(self):
        self.cooldown = self.weapon.cooldown

    def hit(self):
        self.lives -= 1
        self.invincible = 90

    def is_dead(self):
        return self.lives <= 0

    def draw(self, screen, look_at=None):
        # Clignote quand elle est invincible
        if self.invincible > 0 and (self.invincible // 6) % 2 == 0:
            return

        cx = self.rect.centerx
        top = self.rect.y

        # Direction du regard
        ox, oy = 0, 0
        if look_at:
            dx, dy = look_at[0] - cx, look_at[1] - (top + 11)
            dist = math.hypot(dx, dy)
            if dist > 0:
                ox, oy = dx / dist * 1.5, dy / dist * 1.5

        # Jambes et chaussures
        for lx in (cx - 4, cx + 4):
            pygame.draw.line(screen, PEAU, (lx, top + 33), (lx, top + 38), 3)
            pygame.draw.rect(screen, CHAUSSURE, (lx - 3, top + 37, 7, 3))

        # Bras
        pygame.draw.line(screen, PEAU, (cx - 5, top + 22), (cx - 11, top + 29), 3)
        pygame.draw.line(screen, PEAU, (cx + 5, top + 22), (cx + 11, top + 29), 3)

        # Robe
        pygame.draw.polygon(screen, ROBE, [
            (cx - 4, top + 20), (cx + 4, top + 20),
            (cx + 12, top + 34), (cx - 12, top + 34)])

        # Cheveux (derrière) et couettes
        pygame.draw.circle(screen, CHEVEUX, (cx, top + 10), 11)
        for px in (cx - 12, cx + 12):
            pygame.draw.circle(screen, CHEVEUX, (px, top + 15), 4)
            pygame.draw.circle(screen, ROUGE, (px, top + 10), 3)   # nœud

        # Visage
        pygame.draw.circle(screen, PEAU, (cx, top + 11), 9)

        # Frange
        pygame.draw.ellipse(screen, CHEVEUX, (cx - 10, top, 20, 8))

        # Yeux
        for ex in (cx - 4, cx + 4):
            pygame.draw.circle(screen, BLANC, (ex, top + 11), 3)
            pygame.draw.circle(screen, NOIR, (int(ex + ox), int(top + 11 + oy)), 1)

        # Joues et sourire
        for jx in (cx - 7, cx + 7):
            pygame.draw.circle(screen, ROSE_JOUE, (jx, top + 15), 2)
        pygame.draw.arc(screen, ROUGE, (cx - 3, top + 12, 6, 6), 3.4, 6.0, 1)


# ============================================================
#  Plateau de jeu
#  La logique ne connaît que le contrat Monster : n'importe quel
#  sous-type peut être utilisé sans casser le jeu (LSP).
#  États : "playing", "level_complete", "victory", "game_over"
# ============================================================
class GameBoard:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width, self.height = width, height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Jeu de tir - version SOLID")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 32)
        self.big_font = pygame.font.SysFont(None, 56)
        self.monster_renderer = MonsterRenderer()
        self.health_bar = HealthBarRenderer()
        self.high_score = 0
        self.running = True
        self.start_game()

    # ---------- Gestion des niveaux ----------
    def start_game(self):
        """Nouvelle partie : retour au niveau 1."""
        self.level_index = 0
        self.level_start_score = 0
        self.load_level()

    def load_level(self):
        """Charge (ou recharge) le niveau courant."""
        self.config = LEVELS[self.level_index]
        self.player = Player()
        self.monsters = []
        self.bullets = []
        self.enemy_bullets = []
        self.score = self.level_start_score
        self.kills = 0
        self.state = "playing"
        self.paused = False
        for _ in range(self.config.start_monsters):
            self.spawn_monster()

    def next_level(self):
        self.level_index += 1
        self.level_start_score = self.score
        self.load_level()

    def is_last_level(self):
        return self.level_index == len(LEVELS) - 1

    def complete_level(self):
        self.high_score = max(self.high_score, self.score)
        self.bullets.clear()
        self.enemy_bullets.clear()
        self.state = "victory" if self.is_last_level() else "level_complete"

    # ---------- Logique ----------
    def spawn_monster(self):
        """Le type est choisi parmi ceux du niveau courant (OCP)."""
        cls = random.choice(self.config.monster_types)
        self.monsters.append(cls(self.width, self.height))

    def nearest_monster(self):
        p = self.player.rect
        return min(
            self.monsters,
            key=lambda m: math.hypot(m.rect.centerx - p.centerx,
                                     m.rect.centery - p.centery),
            default=None)

    def shoot(self):
        target = self.nearest_monster()
        if target and self.player.can_shoot():
            p = self.player.rect
            self.bullets.append(Bullet(p.centerx, p.centery,
                                       target.rect.centerx,
                                       target.rect.centery,
                                       self.player.weapon))
            self.player.shoot()

    def hurt_player(self):
        self.player.hit()
        if self.player.is_dead():
            self.state = "game_over"
            self.high_score = max(self.high_score, self.score)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_p and self.state == "playing":
                    self.paused = not self.paused
                if event.key == pygame.K_1:
                    self.player.select_weapon(0)
                if event.key == pygame.K_2:
                    self.player.select_weapon(1)
                # Navigation entre les écrans
                if self.state == "game_over" and event.key == pygame.K_r:
                    self.load_level()                # réessayer ce niveau
                if (self.state == "level_complete"
                        and event.key in (pygame.K_RETURN, pygame.K_SPACE)):
                    self.next_level()                # niveau suivant
                if (self.state == "victory"
                        and event.key in (pygame.K_RETURN, pygame.K_r)):
                    self.start_game()                # rejouer depuis le début

    def update(self):
        if self.state != "playing" or self.paused:
            return

        keys = pygame.key.get_pressed()
        screen_rect = self.screen.get_rect()
        self.player.update(screen_rect, keys)

        if keys[pygame.K_SPACE]:
            self.shoot()

        # Chaque monstre applique son propre comportement (LSP)
        for monster in self.monsters:
            self.enemy_bullets.extend(monster.update(self.player.rect))

        # Monstres contre joueur
        for monster in self.monsters[:]:
            if (self.player.invincible == 0
                    and self.player.rect.colliderect(monster.rect)):
                self.monsters.remove(monster)
                self.spawn_monster()
                self.hurt_player()
                break

        # Projectiles ennemis contre joueur
        for eb in self.enemy_bullets[:]:
            eb.update()
            if eb.is_out(screen_rect):
                self.enemy_bullets.remove(eb)
            elif (self.player.invincible == 0
                  and eb.get_rect().colliderect(self.player.rect)):
                self.enemy_bullets.remove(eb)
                self.hurt_player()

        if self.state != "playing":
            return

        # Balles contre monstres
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_out(screen_rect):
                self.bullets.remove(bullet)
                continue
            for monster in self.monsters[:]:
                if bullet.get_rect().colliderect(monster.rect):
                    self.bullets.remove(bullet)
                    if monster.take_damage(bullet.weapon):
                        self.score += monster.points
                        self.kills += 1
                        self.monsters.remove(monster)
                        # On ne remplace que s'il reste des monstres à tuer
                        if self.kills + len(self.monsters) < self.config.target_kills:
                            self.spawn_monster()
                    break

        # Objectif atteint : niveau gagné
        if self.kills >= self.config.target_kills:
            self.complete_level()

    # ---------- Affichage ----------
    def draw_text(self, text, pos, color=BLANC, font=None):
        self.screen.blit((font or self.font).render(text, True, color), pos)

    def draw_centered(self, text, y, color=BLANC, font=None):
        surf = (font or self.font).render(text, True, color)
        self.screen.blit(surf, (self.width // 2 - surf.get_width() // 2, y))

    def draw(self):
        self.screen.fill(NOIR)

        target = self.nearest_monster()
        look_at = target.rect.center if target else None
        self.player.draw(self.screen, look_at)

        for monster in self.monsters:
            self.monster_renderer.draw(self.screen, monster)
            self.health_bar.draw(self.screen, monster)
        for bullet in self.bullets + self.enemy_bullets:
            bullet.draw(self.screen)

        self.draw_text(f"Score : {self.score}", (10, 10))
        self.draw_text(f"Vies : {self.player.lives}", (10, 40))
        self.draw_text(f"Niveau : {self.level_index + 1}/{len(LEVELS)}"
                       f" - {self.config.name}", (10, 70))
        self.draw_text(f"Objectif : {self.kills}/{self.config.target_kills}",
                       (10, 100), VERT)
        self.draw_text(f"Arme : {self.player.weapon.name} (1/2)", (10, 130),
                       self.player.weapon.color)
        self.draw_text(f"Record : {self.high_score}", (620, 10))

        if self.paused:
            self.draw_centered("PAUSE", 270, BLANC, self.big_font)
        if self.state == "game_over":
            self.draw_centered("GAME OVER", 240, ROUGE, self.big_font)
            self.draw_centered("Appuyez sur R pour réessayer ce niveau", 300, ROUGE)
        if self.state == "level_complete":
            self.draw_centered(f"NIVEAU {self.level_index + 1} TERMINÉ !",
                               240, VERT, self.big_font)
            self.draw_centered("Appuyez sur ENTRÉE pour le niveau suivant", 300, VERT)
        if self.state == "victory":
            self.draw_centered("VICTOIRE !", 220, JAUNE, self.big_font)
            self.draw_centered(f"Score final : {self.score}", 280, JAUNE)
            self.draw_centered("Appuyez sur ENTRÉE pour rejouer", 320, JAUNE)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()


if __name__ == "__main__":
    GameBoard().run()
