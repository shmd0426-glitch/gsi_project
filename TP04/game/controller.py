"""CONTRÔLEUR : lit clavier/souris, envoie des commandes au modèle,
gère les états du jeu et fait tourner la boucle principale.

Lancer le jeu :  python controller.py   (ou python main.py)
"""
import pygame

from model import HEIGHT, WIDTH, GameModel
from view import GameView

FPS = 60
# États : "menu", "playing", "paused", "level_complete", "game_over", "victory"


class GameController:
    MENU_ITEMS = ["Jouer", "Quitter"]

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Lila et les cauchemars - MVC")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.model = GameModel()
        self.view = GameView(self.screen, self.model)
        self.state = "menu"
        self.menu_index = 0
        self.running = True

    # ---------- événements ----------
    def start_new_game(self):
        self.model.new_game()
        self.state = "playing"

    def handle_key(self, key):
        m = self.model
        if self.state == "menu":
            if key == pygame.K_ESCAPE:
                self.running = False
            elif key in (pygame.K_UP, pygame.K_DOWN):
                self.menu_index = (self.menu_index + 1) % len(self.MENU_ITEMS)
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.menu_index == 0:
                    self.start_new_game()
                else:
                    self.running = False

        elif self.state == "playing":
            if key in (pygame.K_p, pygame.K_ESCAPE):
                self.state = "paused"
            elif pygame.K_1 <= key <= pygame.K_9:
                m.select_weapon(key - pygame.K_1)

        elif self.state == "paused":
            if key in (pygame.K_p, pygame.K_ESCAPE):
                self.state = "playing"
            elif key == pygame.K_m:
                self.state = "menu"

        elif self.state == "level_complete":
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                m.next_level()
                self.state = "playing"

        elif self.state == "game_over":
            if key == pygame.K_r:
                m.load_level()                    # réessayer ce niveau
                self.state = "playing"
            elif key in (pygame.K_m, pygame.K_ESCAPE):
                self.state = "menu"

        elif self.state == "victory":
            if key in (pygame.K_RETURN, pygame.K_r):
                self.start_new_game()
            elif key in (pygame.K_m, pygame.K_ESCAPE):
                self.state = "menu"

    # ---------- mise à jour ----------
    def update_playing(self):
        m, keys = self.model, pygame.key.get_pressed()
        dx = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) \
            - int(keys[pygame.K_LEFT] or keys[pygame.K_q])
        jump = bool(keys[pygame.K_z] or keys[pygame.K_UP] or keys[pygame.K_w])
        m.set_input(dx, jump)                     # avancer / reculer / sauter

        if pygame.mouse.get_pressed()[0]:         # clic : vers la souris
            mx, my = pygame.mouse.get_pos()
            m.fire((mx + m.camera_x, my))         # écran -> coordonnées du monde
        elif keys[pygame.K_SPACE]:
            m.fire()                              # espace : auto-visée

        m.update()

        if m.player.is_dead():
            m.record_score()
            self.state = "game_over"
        elif m.level_won:
            m.finish_level()
            self.state = "victory" if m.is_last_level() else "level_complete"

    # ---------- affichage ----------
    def draw(self):
        v, m = self.view, self.model
        if self.state == "menu":
            v.draw_menu(self.MENU_ITEMS, self.menu_index)
            return
        v.draw_scene()
        if self.state == "paused":
            v.draw_banner("PAUSE", ["P / Échap : reprendre", "M : menu"])
        elif self.state == "level_complete":
            v.draw_banner(f"HEURE {m.level_index + 1} SURVÉCUE !",
                          [f"Score : {m.player.score}", "ENTRÉE : heure suivante"],
                          (40, 200, 90))
        elif self.state == "game_over":
            v.draw_banner("LES CAUCHEMARS ONT GAGNÉ",
                          [f"Score : {m.player.score}",
                           "R : réessayer le niveau   |   M : menu"], (230, 50, 50))
        elif self.state == "victory":
            v.draw_banner("LE SOLEIL SE LÈVE !",
                          [f"Score final : {m.player.score}",
                           "ENTRÉE : rejouer   |   M : menu"], (255, 220, 0))

    # ---------- boucle principale ----------
    def step(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_key(event.key)
        if self.state == "playing":
            self.update_playing()
        self.draw()
        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.step()
        pygame.quit()


if __name__ == "__main__":
    GameController().run()
