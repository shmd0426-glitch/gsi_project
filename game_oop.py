import math
import random
import pygame

# Couleurs
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
BLEU = (40, 120, 255)
ROUGE = (230, 50, 50)
ORANGE = (255, 150, 0)
VIOLET = (170, 90, 220)
VERT = (40, 200, 90)
JAUNE = (255, 220, 0)

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


class Player:
    """Petite poupée : couettes, robe rose, yeux qui suivent la cible."""

    def __init__(self):
        self.rect = pygame.Rect(386, 500, 28, 40)
        self.speed = 5
        self.lives = 3
        self.cooldown = 0
        self.invincible = 0

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
        self.cooldown = 12

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


class Monster:
    """Petit monstre de base : 1 point de vie."""
    SIZE = 32
    COLOR = ROUGE
    SPEED = 2
    HP = 1
    POINTS = 10

    def __init__(self, width, height):
        x, y = spawn_on_edge(width, height, self.SIZE)
        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE)
        self.speed = self.SPEED
        self.hp = self.HP
        self.max_hp = self.HP
        self.points = self.POINTS

    def chase(self, target_rect):
        dx = target_rect.centerx - self.rect.centerx
        dy = target_rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance > 0:
            self.rect.x += round(dx / distance * self.speed)
            self.rect.y += round(dy / distance * self.speed)

    def take_hit(self):
        """Retourne True si le monstre est détruit."""
        self.hp -= 1
        return self.hp <= 0

    def draw(self, screen):
        r = self.rect

        # Corps arrondi
        body = pygame.Rect(r.x, r.y, r.w, int(r.h * 0.8))
        pygame.draw.rect(screen, self.COLOR, body, border_radius=r.w // 3)

        # Petits pieds
        foot_w = max(4, r.w // 4)
        foot_y = r.y + int(r.h * 0.7)
        foot_h = r.h - int(r.h * 0.7)
        for i in range(3):
            fx = r.x + i * (r.w - foot_w) // 2
            pygame.draw.rect(screen, self.COLOR, (fx, foot_y, foot_w, foot_h))

        # Yeux
        eye_y = r.y + r.h // 3
        eye_r = max(3, r.w // 6)
        for ex in (r.x + r.w // 3, r.x + 2 * r.w // 3):
            pygame.draw.circle(screen, BLANC, (ex, eye_y), eye_r)
            pygame.draw.circle(screen, NOIR, (ex, eye_y), max(1, eye_r // 2))

        # Barre de vie
        if self.max_hp > 1:
            w = r.width * self.hp / self.max_hp
            pygame.draw.rect(screen, VERT, (r.x, r.y - 8, w, 4))


class FastMonster(Monster):
    """Hérite de Monster : minuscule et rapide."""
    SIZE = 24
    COLOR = ORANGE
    SPEED = 4
    POINTS = 20


class TankMonster(Monster):
    """Hérite de Monster : plus gros, lent, 3 points de vie."""
    SIZE = 48
    COLOR = VIOLET
    SPEED = 1
    HP = 3
    POINTS = 30


class Bullet:
    def __init__(self, x, y, target_x, target_y, speed=9):
        dx, dy = target_x - x, target_y - y
        distance = math.hypot(dx, dy) or 1
        self.x, self.y = float(x), float(y)
        self.vx = dx / distance * speed
        self.vy = dy / distance * speed

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def get_rect(self):
        return pygame.Rect(int(self.x) - 4, int(self.y) - 4, 8, 8)

    def is_out(self, screen_rect):
        return not screen_rect.colliderect(self.get_rect())

    def draw(self, screen):
        pygame.draw.circle(screen, JAUNE, (int(self.x), int(self.y)), 4)


class GameBoard:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width, self.height = width, height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Jeu de tir - version POO")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 32)
        self.big_font = pygame.font.SysFont(None, 56)
        self.high_score = 0
        self.running = True
        self.reset()

    # ---------- Logique ----------
    def reset(self):
        self.player = Player()
        self.monsters = []
        self.bullets = []
        self.score = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        for _ in range(2):
            self.spawn_monster()

    def spawn_monster(self):
        """Le type de monstre dépend du niveau."""
        choices = [Monster]
        if self.level >= 2:
            choices.append(FastMonster)
        if self.level >= 3:
            choices.append(TankMonster)
        self.monsters.append(random.choice(choices)(self.width, self.height))

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
                                       target.rect.centery))
            self.player.shoot()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_p and not self.game_over:
                    self.paused = not self.paused
                if event.key == pygame.K_r and self.game_over:
                    self.reset()

    def update(self):
        if self.game_over or self.paused:
            return

        keys = pygame.key.get_pressed()
        screen_rect = self.screen.get_rect()
        self.player.update(screen_rect, keys)

        if keys[pygame.K_SPACE]:
            self.shoot()

        for monster in self.monsters:
            monster.chase(self.player.rect)

        # Monstres contre joueur
        for monster in self.monsters[:]:
            if (self.player.invincible == 0
                    and self.player.rect.colliderect(monster.rect)):
                self.player.hit()
                self.monsters.remove(monster)
                self.spawn_monster()
                if self.player.is_dead():
                    self.game_over = True
                    self.high_score = max(self.high_score, self.score)
                break

        # Balles contre monstres
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_out(screen_rect):
                self.bullets.remove(bullet)
                continue
            for monster in self.monsters[:]:
                if bullet.get_rect().colliderect(monster.rect):
                    self.bullets.remove(bullet)
                    if monster.take_hit():
                        self.score += monster.points
                        self.monsters.remove(monster)
                        self.spawn_monster()
                    break

        # Montée de niveau tous les 100 points
        new_level = self.score // 100 + 1
        if new_level > self.level:
            self.level = new_level
            self.spawn_monster()

    # ---------- Affichage ----------
    def draw_text(self, text, pos, color=BLANC, font=None):
        self.screen.blit((font or self.font).render(text, True, color), pos)

    def draw(self):
        self.screen.fill(NOIR)

        target = self.nearest_monster()
        look_at = target.rect.center if target else None
        self.player.draw(self.screen, look_at)

        for monster in self.monsters:
            monster.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)

        self.draw_text(f"Score : {self.score}", (10, 10))
        self.draw_text(f"Vies : {self.player.lives}", (10, 40))
        self.draw_text(f"Niveau : {self.level}", (10, 70))
        self.draw_text(f"Record : {self.high_score}", (620, 10))

        if self.paused:
            self.draw_text("PAUSE", (330, 270), BLANC, self.big_font)
        if self.game_over:
            self.draw_text("GAME OVER", (280, 240), ROUGE, self.big_font)
            self.draw_text("Appuyez sur R pour recommencer", (240, 300), ROUGE)

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