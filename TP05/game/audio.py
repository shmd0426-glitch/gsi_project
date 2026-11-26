"""SON : lit les musiques et les effets sonores du dossier assets/sounds/.

Le modèle ne joue jamais de son : il note seulement des événements ("shoot",
"jump", "kill"...) et le contrôleur les envoie ici. Si la carte son est
absente, le jeu continue en silence (aucune erreur).

Pour changer un son : remplace le fichier correspondant dans assets/sounds/
(.wav, .ogg ou .mp3, même nom de base).
"""
from pathlib import Path

import pygame

SOUND_DIR = Path(__file__).parent / "assets" / "sounds"
EXTENSIONS = (".wav", ".ogg", ".mp3")

# Volume de chaque effet (0 à 1) : le tir revient souvent, on le garde discret
EFFECTS = {"shoot": 0.35, "jump": 0.5, "hit": 0.5, "kill": 0.7, "stomp": 0.7,
           "pickup": 0.6, "hurt": 0.8, "spawn": 0.7, "win": 0.8, "lose": 0.8}
MUSIC_VOLUME = 0.40


def _find(name):
    for ext in EXTENSIONS:
        path = SOUND_DIR / (name + ext)
        if path.exists():
            return path
    return None


class AudioManager:
    def __init__(self):
        self.enabled = False
        self.muted = False
        self.current = None                 # musique en cours
        self.paused = False
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error as err:
            print("Son indisponible :", err)
            return
        for name, volume in EFFECTS.items():
            path = _find(name)
            if path:
                sound = pygame.mixer.Sound(str(path))
                sound.set_volume(volume)
                self.sounds[name] = sound
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        self.enabled = True

    # ---------- effets ----------
    def play(self, name):
        if self.enabled and not self.muted and name in self.sounds:
            self.sounds[name].play()

    # ---------- musique de fond ----------
    def play_music(self, name):
        """Lance la musique `name` en boucle (ne fait rien si elle joue déjà)."""
        if not self.enabled:
            return
        if name == self.current:
            if self.paused:
                pygame.mixer.music.unpause()
                self.paused = False
            return
        path = _find(name)
        self.current, self.paused = name, False
        if path is None:
            pygame.mixer.music.stop()
            return
        pygame.mixer.music.load(str(path))
        pygame.mixer.music.set_volume(0 if self.muted else MUSIC_VOLUME)
        pygame.mixer.music.play(-1)         # -1 = en boucle

    def pause_music(self):
        if self.enabled and self.current and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True

    def stop_music(self):
        if self.enabled:
            pygame.mixer.music.stop()
        self.current, self.paused = None, False

    def toggle_mute(self):
        self.muted = not self.muted
        if self.enabled:
            pygame.mixer.music.set_volume(0 if self.muted else MUSIC_VOLUME)
        return self.muted