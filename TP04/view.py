"""VUE : lit l'état du modèle et dessine. Ne modifie jamais le modèle.

Décor en couches (parallaxe) : plus une couche est loin, plus elle défile
lentement, ce qui donne l'effet de profondeur des jeux vidéo.
"""
import math
import random
from pathlib import Path

import pygame

from model import (BLANC, CYAN, GRIS, GROUND_Y, HEIGHT, JAUNE, LEVELS, NOIR,
                   ORANGE, ROSE, ROUGE, VERT, WIDTH)

# ============================================================
#  Thèmes de décor (un par niveau)
# ============================================================
THEMES = {
    "sunset": dict(seed=11, sky=((70, 45, 120), (225, 95, 110), (255, 190, 110)),
                   far=(132, 76, 130), mid=(98, 56, 112), trees_far=(74, 44, 98),
                   trees=(48, 30, 74), grass=(112, 205, 88), grass_dark=(70, 150, 70),
                   dirt=(128, 82, 60), dirt_dark=(94, 60, 48), cloud=(255, 190, 160),
                   body="sun", body_color=(255, 200, 110), body_pos=(570, 330),
                   stars=0, fireflies=0),
    "night": dict(seed=22, sky=((6, 8, 34), (22, 28, 78), (58, 62, 120)),
                  far=(34, 44, 98), mid=(24, 32, 78), trees_far=(18, 26, 66),
                  trees=(10, 14, 42), grass=(58, 150, 105), grass_dark=(36, 105, 84),
                  dirt=(66, 52, 70), dirt_dark=(46, 36, 54), cloud=(90, 100, 160),
                  body="moon", body_color=(240, 240, 215), body_pos=(630, 105),
                  stars=110, fireflies=26),
    "dawn": dict(seed=33, sky=((84, 104, 178), (238, 150, 172), (255, 222, 156)),
                 far=(158, 126, 176), mid=(116, 104, 156), trees_far=(88, 90, 136),
                 trees=(56, 66, 108), grass=(124, 210, 116), grass_dark=(80, 160, 90),
                 dirt=(134, 94, 76), dirt_dark=(100, 68, 58), cloud=(255, 215, 200),
                 body="sun", body_color=(255, 238, 170), body_pos=(230, 385),
                 stars=30, fireflies=12),
}

PEAU, CHEVEUX = (255, 214, 170), (120, 66, 34)
ROBE, ROBE_FONCEE = (255, 105, 180), (224, 78, 150)
CHAUSSURE, CONTOUR = (160, 34, 66), (70, 35, 50)


def _gradient(top, mid, bottom):
    surf = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        a, b, k = (top, mid, t / 0.55) if t < 0.55 else (mid, bottom, (t - 0.55) / 0.45)
        pygame.draw.line(surf, tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3)),
                         (0, y), (WIDTH, y))
    return surf


def _lerp(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


# ============================================================
#  Décor : ciel, astre, nuages, montagnes, forêt, sol
# ============================================================
class Background:
    def __init__(self, name):
        th = self.th = THEMES[name]
        rng = random.Random(th["seed"])
        self.sky = self._make_sky(rng)
        self.far = self._ridge(1400, 365, [(2, 55, 0.4), (5, 22, 1.7), (11, 8, 2.9)],
                               th["far"], pointy=True)
        self.mid = self._ridge(1100, 430, [(1, 34, 2.1), (3, 18, 0.6), (7, 7, 1.1)],
                               th["mid"])
        self.trees_far = self._forest(900, GROUND_Y + 2, 55, 85, (46, 70), th["trees_far"], rng)
        self.trees = self._forest(1000, GROUND_Y + 6, 85, 140, (60, 110), th["trees"], rng)
        self.clouds = [(rng.randint(0, WIDTH + 400), rng.randint(40, 230),
                        rng.choice([0.7, 1.0, 1.4])) for _ in range(7)]
        self.cloud_img = self._cloud(th["cloud"])
        self.flies = [(rng.randint(0, WIDTH), rng.randint(250, GROUND_Y - 20),
                       rng.random() * 6.3) for _ in range(th["fireflies"])]
        self.glow = pygame.Surface((14, 14), pygame.SRCALPHA)
        for r in range(7, 0, -1):
            pygame.draw.circle(self.glow, (255, 240, 150, 30 + (7 - r) * 28), (7, 7), r)

    # ----- fabrication des couches -----
    def _make_sky(self, rng):
        th = self.th
        sky = _gradient(*th["sky"])
        for _ in range(th["stars"]):
            x, y = rng.randrange(WIDTH), rng.randrange(0, 330)
            c = rng.choice([(255, 255, 255), (200, 210, 255), (255, 240, 200)])
            sky.set_at((x, y), c)
            if rng.random() < 0.25:
                pygame.draw.circle(sky, c, (x, y), 1)
        x, y = th["body_pos"]
        glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for r in range(130, 40, -6):
            pygame.draw.circle(glow, (*th["body_color"], min(120, int(10 + (130 - r) * 1.1))),
                               (x, y), r)
        sky.blit(glow, (0, 0))
        pygame.draw.circle(sky, th["body_color"], (x, y), 40)
        if th["body"] == "moon":                          # cratères
            for dx, dy, r in [(-12, -8, 8), (14, 10, 6), (-4, 18, 5), (16, -14, 4)]:
                pygame.draw.circle(sky, (205, 205, 185), (x + dx, y + dy), r)
        return sky

    def _ridge(self, T, base, waves, color, pointy=False):
        surf = pygame.Surface((T, HEIGHT), pygame.SRCALPHA)
        pts = [(0, HEIGHT)]
        for x in range(0, T + 1, 6):
            y = base
            for freq, amp, ph in waves:
                s = math.sin(2 * math.pi * freq * x / T + ph)
                y += -amp * abs(s) if pointy else amp * s
            pts.append((x, y))
        pts.append((T, HEIGHT))
        pygame.draw.polygon(surf, color, pts)
        return surf

    def _forest(self, T, base, hmin, hmax, gap, color, rng):
        surf = pygame.Surface((T, HEIGHT), pygame.SRCALPHA)
        x = rng.randint(0, 30)
        while x < T:
            h = rng.randint(hmin, hmax)
            for ox in (0, -T, T):                          # boucle sans coupure
                cx, w = x + ox, h * 0.5
                pygame.draw.rect(surf, color, (cx - 3, base - 14, 6, 14))
                for i in range(3):
                    top = base - h + i * h * 0.22
                    wi = w * (0.55 + 0.25 * i)
                    pygame.draw.polygon(surf, color, [(cx, top), (cx - wi / 2, top + h * 0.4),
                                                      (cx + wi / 2, top + h * 0.4)])
            x += rng.randint(*gap)
        return surf

    def _cloud(self, color):
        surf = pygame.Surface((170, 60), pygame.SRCALPHA)
        c = (*color, 150)
        for cx, cy, w, h in [(40, 38, 70, 34), (80, 28, 76, 40), (122, 38, 66, 32),
                             (85, 42, 130, 26)]:
            pygame.draw.ellipse(surf, c, (cx - w // 2, cy - h // 2, w, h))
        return surf

    # ----- affichage -----
    @staticmethod
    def _tile(screen, surf, factor, cam):
        T = surf.get_width()
        x = -int(cam * factor) % T - T
        while x < WIDTH:
            screen.blit(surf, (x, 0))
            x += T

    def draw(self, screen, cam, t):
        screen.blit(self.sky, (0, 0))
        span = WIDTH + 400
        for cx, cy, scale in self.clouds:
            sx = (cx - cam * 0.1 - t * 0.25 * scale) % span - 200
            img = self.cloud_img if scale == 1.0 else pygame.transform.rotozoom(self.cloud_img, 0, scale)
            screen.blit(img, (sx, cy))
        self._tile(screen, self.far, 0.08, cam)
        self._tile(screen, self.mid, 0.2, cam)
        self._tile(screen, self.trees_far, 0.35, cam)
        self._tile(screen, self.trees, 0.6, cam)
        for bx, by, ph in self.flies:                       # lucioles
            fx = (bx - cam * 0.7 + math.sin(t * 0.02 + ph) * 25) % WIDTH
            fy = by + math.sin(t * 0.035 + ph) * 18
            if math.sin(t * 0.07 + ph * 3) > -0.3:
                screen.blit(self.glow, (fx - 7, fy - 7))


# ============================================================
#  Poupée dessinée en pixels (animée : marche, saut)
# ============================================================
def _blob(s, color, center, r):
    pygame.draw.circle(s, CONTOUR, center, r + 1)
    pygame.draw.circle(s, color, center, r)


def _limb(s, color, a, b, width):
    pygame.draw.line(s, CONTOUR, a, b, width + 2)
    pygame.draw.line(s, color, a, b, width)


def build_doll(phase=0.0, airborne=False):
    """Retourne l'image de la poupée tournée vers la droite (60x76)."""
    s = pygame.Surface((60, 76), pygame.SRCALPHA)
    cx = 30
    swing = 0 if airborne else math.sin(phase) * 7
    b = 0 if airborne else int(-abs(math.sin(phase)) * 2)      # petit rebond
    foot = 73

    # Jambes (celle de derrière en premier)
    if airborne:
        legs = [((cx - 4, 54 + b), (cx - 10, 66)), ((cx + 4, 54 + b), (cx + 8, 64))]
    else:
        legs = [((cx - 3, 54 + b), (cx - 3 - swing, foot - 4)),
                ((cx + 4, 54 + b), (cx + 4 + swing, foot - 4))]
    for a, e in legs:
        _limb(s, PEAU, a, e, 4)
        pygame.draw.ellipse(s, CONTOUR, (e[0] - 6, e[1] - 1, 13, 8))
        pygame.draw.ellipse(s, CHAUSSURE, (e[0] - 5, e[1], 11, 6))

    # Bras arrière
    back = (cx - 9 + swing * 0.9, 53 + b) if not airborne else (cx - 14, 40 + b)
    _limb(s, PEAU, (cx - 6, 43 + b), back, 4)

    # Robe : jupe + ruban + volants
    pygame.draw.polygon(s, CONTOUR, [(cx - 8, 38 + b), (cx + 8, 38 + b),
                                     (cx + 19, 60 + b), (cx - 19, 60 + b)])
    pygame.draw.polygon(s, ROBE, [(cx - 7, 39 + b), (cx + 7, 39 + b),
                                  (cx + 17, 59 + b), (cx - 17, 59 + b)])
    pygame.draw.polygon(s, ROBE_FONCEE, [(cx - 12, 51 + b), (cx + 12, 51 + b),
                                         (cx + 17, 59 + b), (cx - 17, 59 + b)])
    for i in range(5):                                           # volant festonné
        pygame.draw.circle(s, (255, 170, 215), (cx - 16 + i * 8, 59 + b), 4)
    pygame.draw.rect(s, (255, 235, 120), (cx - 8, 42 + b, 16, 4))   # ceinture
    for dx, dy in [(-6, 50), (4, 47), (9, 55), (-10, 56)]:           # petits pois
        pygame.draw.circle(s, (255, 255, 255), (cx + dx, dy + b), 1)

    # Bras avant (tend l'arme vers l'avant)
    _limb(s, PEAU, (cx + 6, 43 + b), (cx + 17, 46 + b), 4)

    # Cheveux arrière + couettes avec nœuds
    _blob(s, CHEVEUX, (cx, 24 + b), 17)
    for px in (cx - 16, cx + 15):
        _blob(s, CHEVEUX, (px, 34 + b), 6)
        pygame.draw.polygon(s, ROUGE, [(px, 29 + b), (px - 6, 24 + b), (px - 6, 33 + b)])
        pygame.draw.polygon(s, ROUGE, [(px, 29 + b), (px + 6, 24 + b), (px + 6, 33 + b)])
        pygame.draw.circle(s, (255, 90, 90), (px, 29 + b), 2)

    # Visage (légèrement tourné vers la droite)
    _blob(s, PEAU, (cx + 1, 28 + b), 13)
    for ex in (cx + 3, cx + 11):
        pygame.draw.ellipse(s, BLANC, (ex - 3, 24 + b, 7, 9))
        pygame.draw.ellipse(s, (60, 90, 170), (ex - 1, 26 + b, 5, 7))
        pygame.draw.circle(s, NOIR, (ex + 1, 29 + b), 1)
        pygame.draw.circle(s, BLANC, (ex, 26 + b), 1)
    pygame.draw.circle(s, (255, 150, 150), (cx + 13, 33 + b), 2)
    pygame.draw.circle(s, (255, 150, 150), (cx - 2, 33 + b), 2)
    pygame.draw.arc(s, ROUGE, (cx + 4, 31 + b, 8, 6), 3.5, 5.9, 1)

    # Frange
    pygame.draw.ellipse(s, CONTOUR, (cx - 14, 10 + b, 29, 15))
    pygame.draw.ellipse(s, CHEVEUX, (cx - 13, 11 + b, 27, 13))
    for dx in (-8, 0, 8):
        pygame.draw.polygon(s, CHEVEUX, [(cx + dx - 4, 20 + b), (cx + dx + 4, 20 + b),
                                         (cx + dx, 26 + b)])
    return s


# ============================================================
#  Vue principale
# ============================================================
class GameView:
    def __init__(self, screen, model):
        self.screen, self.model = screen, model
        self.font = pygame.font.SysFont(None, 28)
        self.small = pygame.font.SysFont(None, 22)
        self.big = pygame.font.SysFont(None, 56)
        self.huge = pygame.font.SysFont(None, 76)
        self.t = 0
        self.backgrounds, self.prepared = {}, None
        self.decor, self.plat_cache, self.ground_tiles = [], {}, {}

        # Images de la poupée (marche à 4 phases + saut), retournées pour la gauche
        phases = [0, math.pi / 2, math.pi, 3 * math.pi / 2]
        self.walk = [build_doll(p) for p in phases]
        self.idle, self.jump = build_doll(0.3), build_doll(0, airborne=True)
        self.custom = self._load_custom()        # assets/player.png (facultatif)

        self.shadow = pygame.Surface((80, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(self.shadow, (0, 0, 0, 90), (0, 0, 80, 14))

    def _load_custom(self):
        """Si tu ajoutes ta propre image assets/player.png, elle remplace la poupée."""
        path = Path(__file__).parent / "assets" / "player.png"
        if not path.exists():
            return None
        try:
            img = pygame.image.load(str(path)).convert_alpha()
            h = 76
            return pygame.transform.smoothscale(img, (int(img.get_width() * h / img.get_height()), h))
        except pygame.error:
            return None

    # ---------- préparation d'un niveau ----------
    def _prepare(self, theme_name, level_index, length):
        if theme_name not in self.backgrounds:
            self.backgrounds[theme_name] = Background(theme_name)
        self.bg = self.backgrounds[theme_name]
        th = self.th = THEMES[theme_name]
        if theme_name not in self.ground_tiles:
            self.ground_tiles[theme_name] = self._make_ground_tile(th)
        rng = random.Random(level_index + 100)
        self.decor, x = [], 150
        while x < length:
            self.decor.append((x, rng.choice(["flower", "tuft", "tuft", "mushroom", "rock"]),
                               rng.choice([(255, 120, 150), (255, 230, 90), (255, 255, 255),
                                           (150, 170, 255)])))
            x += rng.randint(70, 190)
        self.prepared = (theme_name, level_index)

    def _make_ground_tile(self, th):
        h = HEIGHT - GROUND_Y + 8
        t = pygame.Surface((128, h), pygame.SRCALPHA)
        for y in range(8, h):                                    # terre dégradée
            pygame.draw.line(t, _lerp(th["dirt"], th["dirt_dark"], (y - 8) / h), (0, y), (128, y))
        rng = random.Random(5)
        for _ in range(16):                                      # cailloux
            r = rng.randint(2, 5)
            pygame.draw.ellipse(t, rng.choice([th["dirt_dark"], _lerp(th["dirt"], BLANC, 0.18)]),
                                (rng.randint(0, 120), rng.randint(30, h - 8), r * 2, r))
        pygame.draw.rect(t, th["grass"], (0, 8, 128, 14))
        pygame.draw.rect(t, th["grass_dark"], (0, 20, 128, 4))
        for bx in range(0, 128, 8):                              # brins d'herbe
            pygame.draw.polygon(t, th["grass"], [(bx, 9), (bx + 4, rng.randint(0, 5)), (bx + 8, 9)])
        return t

    def _platform_image(self, w):
        key = (self.prepared[0], w)
        if key not in self.plat_cache:
            th = self.th
            s = pygame.Surface((w, 30), pygame.SRCALPHA)
            pygame.draw.rect(s, CONTOUR, (0, 6, w, 24), border_radius=5)
            pygame.draw.rect(s, th["dirt"], (2, 8, w - 4, 20), border_radius=4)
            for bx in range(0, w, 26):                           # briques
                pygame.draw.line(s, th["dirt_dark"], (bx, 14), (bx, 27), 2)
            pygame.draw.line(s, th["dirt_dark"], (2, 20), (w - 2, 20), 2)
            pygame.draw.rect(s, th["grass"], (0, 4, w, 9), border_radius=4)
            pygame.draw.rect(s, th["grass_dark"], (2, 11, w - 4, 3))
            for bx in range(4, w - 6, 9):
                pygame.draw.polygon(s, th["grass"], [(bx, 6), (bx + 4, 0), (bx + 8, 6)])
            self.plat_cache[key] = s
        return self.plat_cache[key]

    # ---------- outils texte ----------
    def _text(self, text, pos, color=BLANC, font=None):
        font = font or self.font
        self.screen.blit(font.render(text, True, (0, 0, 0)), (pos[0] + 1, pos[1] + 1))
        self.screen.blit(font.render(text, True, color), pos)

    def _centered(self, text, y, color=BLANC, font=None):
        font = font or self.font
        surf = font.render(text, True, color)
        x = WIDTH // 2 - surf.get_width() // 2
        self.screen.blit(font.render(text, True, (0, 0, 0)), (x + 2, y + 2))
        self.screen.blit(surf, (x, y))

    # ---------- éléments du monde ----------
    def _draw_ground(self, cam, limit=None):
        tile = self.ground_tiles[self.prepared[0]]
        for x in range((int(cam) // 128) * 128, int(cam) + WIDTH + 128, 128):
            if limit is None or x < limit:
                self.screen.blit(tile, (x - int(cam), GROUND_Y - 8))

    def _draw_decor(self, cam):
        s, gy = self.screen, GROUND_Y
        for x, kind, color in self.decor:
            sx = x - cam
            if not -30 < sx < WIDTH + 30:
                continue
            if kind == "flower":
                pygame.draw.line(s, self.th["grass_dark"], (sx, gy), (sx, gy - 13), 2)
                pygame.draw.circle(s, color, (sx, gy - 15), 4)
                pygame.draw.circle(s, JAUNE, (sx, gy - 15), 1)
            elif kind == "tuft":
                for dx in (-4, 0, 4):
                    pygame.draw.line(s, self.th["grass"], (sx + dx, gy), (sx + dx * 2, gy - 11), 2)
            elif kind == "mushroom":
                cap = (255, 90, 90) if self.th["body"] == "sun" else (110, 230, 255)
                pygame.draw.rect(s, (240, 230, 210), (sx - 2, gy - 8, 5, 8))
                pygame.draw.ellipse(s, cap, (sx - 8, gy - 17, 16, 11))
                pygame.draw.circle(s, BLANC, (sx - 3, gy - 13), 2)
                pygame.draw.circle(s, BLANC, (sx + 3, gy - 12), 1)
            else:
                pygame.draw.ellipse(s, (110, 110, 125), (sx - 9, gy - 9, 18, 11))
                pygame.draw.ellipse(s, (150, 150, 165), (sx - 6, gy - 9, 10, 5))
        m = self.model                                           # panneaux de distance
        for x in range(1000, int(m.length) - 300, 1000):
            sx = x - cam
            if -40 < sx < WIDTH + 40:
                pygame.draw.rect(s, (92, 58, 36), (sx - 3, gy - 46, 6, 46))
                pygame.draw.rect(s, (170, 118, 70), (sx - 30, gy - 62, 60, 24), border_radius=4)
                pygame.draw.rect(s, (92, 58, 36), (sx - 30, gy - 62, 60, 24), 2, border_radius=4)
                label = self.small.render(f"{x // 100} m", True, (60, 36, 20))
                s.blit(label, label.get_rect(center=(sx, gy - 50)))

    def _draw_flag(self, cam):
        sx, gy, t = self.model.flag_x - cam, GROUND_Y, self.t
        if not -60 < sx < WIDTH + 60:
            return
        s = self.screen
        pygame.draw.ellipse(s, (100, 100, 110), (sx - 18, gy - 10, 36, 14))
        pygame.draw.rect(s, (225, 225, 235), (sx - 3, gy - 220, 6, 214))
        pygame.draw.rect(s, CONTOUR, (sx - 3, gy - 220, 6, 214), 1)
        pygame.draw.circle(s, JAUNE, (sx, gy - 224), 6)
        top, bottom = [], []
        for i in range(7):
            wave = math.sin(t * 0.1 + i * 0.8) * 4
            top.append((sx + 3 + i * 8, gy - 212 + wave))
            bottom.append((sx + 3 + i * 8, gy - 176 + wave - i * 3))
        pygame.draw.polygon(s, ROSE, top + bottom[::-1])
        pygame.draw.polygon(s, CONTOUR, top + bottom[::-1], 2)
        label = self.small.render("ARRIVÉE", True, BLANC)
        s.blit(label, label.get_rect(center=(sx, gy - 240)))

    def _draw_monster(self, m, cam):
        r, color, f = m.rect.move(-cam, 0), m.color, m.facing
        shadow = pygame.transform.scale(self.shadow, (int(r.w * 1.1), 10))
        self.screen.blit(shadow, (r.centerx - shadow.get_width() // 2, GROUND_Y - 4))
        if m.FLYING:                                            # ailes qui battent
            flap = int(math.sin(self.t * 0.4) * 5)
            wing = pygame.Rect(0, 0, r.w // 2, r.h // 3)
            wing.midright = (r.x + 2, r.y + r.h // 3 - flap)
            pygame.draw.ellipse(self.screen, BLANC, wing)
            wing.midleft = (r.right - 2, r.y + r.h // 3 - flap)
            pygame.draw.ellipse(self.screen, BLANC, wing)
        body = pygame.Rect(r.x, r.y, r.w, int(r.h * 0.8))
        pygame.draw.rect(self.screen, color, body, border_radius=r.w // 3)
        foot_w, foot_y = max(4, r.w // 4), r.y + int(r.h * 0.7)
        for i in range(3):
            pygame.draw.rect(self.screen, color,
                             (r.x + i * (r.w - foot_w) // 2, foot_y, foot_w, r.h - int(r.h * 0.7)))
        eye_y, eye_r = r.y + r.h // 3, max(3, r.w // 6)
        for ex in (r.x + r.w // 3, r.x + 2 * r.w // 3):
            pygame.draw.circle(self.screen, BLANC, (ex, eye_y), eye_r)
            pygame.draw.circle(self.screen, NOIR, (ex + f * (eye_r // 3), eye_y), max(1, eye_r // 2))
        if m.shield_up:
            pygame.draw.circle(self.screen, CYAN, r.center, r.w // 2 + 6, 3)
        ratio = max(0.0, m.hp) / m.max_hp                       # barre de vie
        pygame.draw.rect(self.screen, ROUGE, (r.x, r.y - 8, r.width, 4))
        pygame.draw.rect(self.screen, VERT, (r.x, r.y - 8, r.width * ratio, 4))

    def _draw_reward(self, rw, cam):
        if rw.timer < 120 and (rw.timer // 8) % 2 == 0:
            return
        bob = math.sin(self.t * 0.08 + rw.rect.x) * 3          # flotte doucement
        c = (rw.rect.centerx - cam, rw.rect.centery + bob)
        pygame.draw.circle(self.screen, rw.COLOR, c, rw.SIZE // 2)
        pygame.draw.circle(self.screen, BLANC, c, rw.SIZE // 2, 2)
        label = self.small.render(rw.LABEL, True, NOIR)
        self.screen.blit(label, label.get_rect(center=c))

    def _doll_image(self, p):
        if self.custom:
            return self.custom
        if not p.on_ground:
            return self.jump
        if p.moving:
            return self.walk[int(p.walk_phase * 1.2) % 4]
        return self.idle

    def _draw_player(self, p, cam):
        r = p.rect.move(-cam, 0)
        shadow = pygame.transform.scale(self.shadow, (40, 10))
        self.screen.blit(shadow, (r.centerx - 20, GROUND_Y - 4))
        if p.shielded:
            pygame.draw.circle(self.screen, CYAN, (r.centerx, r.centery), 38, 3)
        if p.invincible > 0 and (p.invincible // 5) % 2 == 0:
            return
        img = self._doll_image(p)
        if p.facing < 0:
            img = pygame.transform.flip(img, True, False)
        self.screen.blit(img, (r.centerx - img.get_width() // 2, r.bottom - img.get_height() + 3))
        # Arme tenue dans la main
        w, f = p.weapon, p.facing
        hand = (r.centerx + f * 17, r.y + 27)
        gun = pygame.Rect(hand[0] if f > 0 else hand[0] - 13, hand[1] - 3, 13, 6)
        pygame.draw.rect(self.screen, CONTOUR, gun.inflate(2, 2), border_radius=2)
        pygame.draw.rect(self.screen, w.color, gun, border_radius=2)
        if p.cooldown >= w.cooldown - 3 and w.cooldown:        # éclair au tir
            pygame.draw.circle(self.screen, (255, 255, 200), (hand[0] + f * 16, hand[1]), 5)

    def _draw_hud(self):
        m, p = self.model, self.model.player
        self._text(f"Score : {p.score}", (10, 10))
        self._text(f"Niveau {m.level_index + 1}/{len(LEVELS)} - {m.config.name}", (10, 36))
        self._text(f"Monstres vaincus : {m.kills}", (10, 62), VERT, self.small)
        ratio = max(0.0, p.health) / p.MAX_HEALTH               # barre de santé
        color = VERT if ratio > 0.5 else ORANGE if ratio > 0.25 else ROUGE
        pygame.draw.rect(self.screen, (0, 0, 0), (9, 86, 164, 20), border_radius=5)
        pygame.draw.rect(self.screen, color, (11, 88, int(160 * ratio), 16), border_radius=4)
        self._text(f"{int(p.health)} PV", (180, 88), color, self.small)
        self._text(f"Record : {m.high_score}", (WIDTH - 150, 10))

        # Barre de progression du niveau (poupée -> drapeau)
        bx, bw = 270, 260
        pygame.draw.rect(self.screen, (0, 0, 0), (bx - 2, 18, bw + 4, 12), border_radius=6)
        pygame.draw.rect(self.screen, (70, 70, 90), (bx, 20, bw, 8), border_radius=4)
        done = max(0.0, min(1.0, p.rect.centerx / m.flag_x))
        pygame.draw.rect(self.screen, ROSE, (bx, 20, int(bw * done), 8), border_radius=4)
        pygame.draw.circle(self.screen, BLANC, (bx + int(bw * done), 24), 7)
        pygame.draw.polygon(self.screen, JAUNE, [(bx + bw + 4, 14), (bx + bw + 4, 28), (bx + bw + 18, 21)])

        x = 10                                                   # armes (touches 1, 2, 3)
        for i, w in enumerate(p.weapons):
            label = f"{i + 1}:{w.name}"
            self._text(label, (x, HEIGHT - 28), w.color if i == p.weapon_index else GRIS)
            x += self.font.size(label)[0] + 18
        y = HEIGHT - 28                                          # effets temporaires
        for name, frames in p.effects.items():
            self._text(f"{'Vitesse' if name == 'speed' else 'Bouclier'} {frames / 60:.0f}s",
                       (WIDTH - 130, y), VERT if name == "speed" else CYAN, self.small)
            y -= 22

    # ---------- écrans ----------
    def draw_scene(self):
        m, cam = self.model, int(self.model.camera_x)
        if self.prepared != (m.config.theme, m.level_index):
            self._prepare(m.config.theme, m.level_index, m.length)
        self.t += 1
        self.bg.draw(self.screen, cam, self.t)
        self._draw_ground(cam, m.length)
        self._draw_decor(cam)
        self._draw_flag(cam)
        for plat in m.platforms[1:]:
            if plat.right > cam and plat.left < cam + WIDTH:
                self.screen.blit(self._platform_image(plat.w), (plat.x - cam, plat.y - 4))
        for rw in m.rewards:
            self._draw_reward(rw, cam)
        for mo in m.monsters:
            if cam - 120 < mo.rect.x < cam + WIDTH + 120:
                self._draw_monster(mo, cam)
        self._draw_player(m.player, cam)
        for b in m.bullets + m.enemy_bullets:
            c = (int(b.x - cam), int(b.y))
            pygame.draw.circle(self.screen, b.color, c, 5)
            pygame.draw.circle(self.screen, BLANC, c, 2)
        for text, x, y, color, _ in m.messages:
            self._text(text, (x - cam, y), color, self.small)
        self._draw_hud()

    def draw_banner(self, title, lines=(), color=BLANC):
        panel = pygame.Surface((WIDTH, 170), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 170))
        self.screen.blit(panel, (0, HEIGHT // 2 - 105))
        self._centered(title, 220, color, self.big)
        for i, line in enumerate(lines):
            self._centered(line, 285 + i * 30, color)

    def draw_menu(self, items, index):
        """Menu animé : la poupée marche dans le décor qui défile."""
        self.t += 1
        cam = self.t * 1.6
        if self.prepared is None or self.prepared[0] != "sunset":
            self._prepare("sunset", 0, 10 ** 7)
        self.bg.draw(self.screen, cam, self.t)
        self._draw_ground(cam)
        self._draw_decor(cam)
        img = self.walk[(self.t // 6) % 4]
        self.screen.blit(pygame.transform.scale(self.shadow, (40, 10)), (WIDTH // 2 - 20, GROUND_Y - 4))
        self.screen.blit(img, (WIDTH // 2 - 30, GROUND_Y - 73))
        self._centered("LILA ET LES CAUCHEMARS", 55, ROSE, self.huge)
        self._centered("Protège le sommeil de l'enfant jusqu'au lever du jour !", 125, BLANC)
        for i, item in enumerate(items):
            sel = i == index
            self._centered(f"> {item} <" if sel else item, 190 + i * 48,
                           JAUNE if sel else BLANC, self.big if sel else self.font)
        self._centered(f"Record : {self.model.high_score}", 300, BLANC, self.small)
        for i, line in enumerate([
                "Q D ou flèches : avancer / reculer   |   Z ou flèche haut : sauter   |   ESPACE ou clic : tirer",
                "Saute sur la tête des monstres pour les écraser   |   1 2 3 : changer d'arme",
                "P / Échap : pause   |   + câlin  $ étoile  S chaussons  B doudou  W canon"]):
            self._centered(line, HEIGHT - 78 + i * 22, BLANC, self.small)