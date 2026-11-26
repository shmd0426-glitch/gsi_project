"""Génère les sons et les musiques du jeu (aucun fichier externe nécessaire).

Lancer :  python make_audio.py
Crée les fichiers .wav dans assets/sounds/ :
  musiques : music_menu, music_classic, music_fantasy, music_space
  effets   : shoot, jump, hit, kill, stomp, pickup, hurt, spawn, win, lose

Pour utiliser TES sons : remplace simplement un fichier .wav (ou .ogg / .mp3,
même nom de base) par le tien dans assets/sounds/.
"""
import wave
from pathlib import Path

import numpy as np

SR = 22050                                   # fréquence d'échantillonnage
OUT = Path(__file__).parent / "assets" / "sounds"


# ---------------------------------------------------------------- outils
def mtof(midi):
    """Numéro de note MIDI -> fréquence en Hz (69 = La 440)."""
    return 440.0 * 2 ** ((midi - 69) / 12)


def osc(kind, phase):
    """Forme d'onde à partir de la phase (en tours) : square, pulse, tri, saw, sine, bell."""
    ph = phase % 1.0
    if kind == "square":
        return np.where(ph < 0.5, 1.0, -1.0)
    if kind == "pulse":
        return np.where(ph < 0.25, 1.0, -1.0)
    if kind == "tri":
        return 2 * np.abs(2 * ph - 1) - 1
    if kind == "saw":
        return 2 * ph - 1
    if kind == "bell":
        w = 2 * np.pi * phase
        return (np.sin(w) + 0.4 * np.sin(2.01 * w) + 0.2 * np.sin(3.99 * w)) / 1.6
    return np.sin(2 * np.pi * phase)


def note(kind, midi, dur, vol=0.3, decay=0.0, attack=0.004, release=0.03, vibrato=0.0):
    """Une note : forme d'onde + enveloppe (attaque, chute, relâchement)."""
    n = max(1, int(dur * SR))
    t = np.arange(n) / SR
    freq = mtof(midi) * (1 + vibrato * np.sin(2 * np.pi * 5.5 * t))   # vibrato léger
    sig = osc(kind, np.cumsum(freq) / SR)
    env = np.minimum(1.0, t / attack) * np.exp(-t * decay)
    env *= np.clip((dur - t) / release, 0.0, 1.0)
    return sig * env * vol


def noise(dur, vol=0.3, decay=20.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(7)
    return rng.uniform(-1, 1, n) * np.exp(-t * decay) * vol


def sweep(kind, f0, f1, dur, vol=0.3, decay=0.0):
    """Note dont la hauteur glisse de f0 à f1 (tirs, sauts...)."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = osc(kind, np.cumsum(np.linspace(f0, f1, n)) / SR)
    env = np.exp(-t * decay) * np.clip((dur - t) / 0.02, 0.0, 1.0)
    return sig * env * vol


def put(buf, start_sec, sig):
    """Ajoute `sig` dans `buf` à partir de start_sec (le morceau reboucle)."""
    i = int(start_sec * SR)
    n = len(sig)
    idx = (np.arange(n) + i) % len(buf)            # boucle sans coupure
    np.add.at(buf, idx, sig)


def echo(buf, delay=0.28, gain=0.35, times=3):
    """Écho qui reboucle : donne de l'espace (monde spatial)."""
    out = buf.copy()
    for k in range(1, times + 1):
        out += np.roll(buf, int(delay * SR * k)) * (gain ** k)
    return out


def save(name, sig, peak=0.8):
    sig = np.asarray(sig, dtype=np.float64)
    m = np.max(np.abs(sig)) or 1.0
    data = (sig / m * peak * 32767).astype(np.int16)
    OUT.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUT / f"{name}.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    print(f"{name}.wav  ({len(data) / SR:.1f} s)")


def track(bpm, bars):
    beat = 60.0 / bpm
    return beat, np.zeros(int(bars * 4 * beat * SR))


# ---------------------------------------------------------------- musiques
def music_menu():
    """Berceuse de boîte à musique."""
    beat, buf = track(84, 8)
    chords = [(60, (0, 4, 7)), (57, (0, 3, 7)), (53, (0, 4, 7)), (55, (0, 4, 7))] * 2
    melody = [  # (temps, durée, note) par mesure
        [(0, 1, 76), (1, 1, 79), (2, 2, 84)], [(0, 1, 81), (1, 1, 79), (2, 2, 76)],
        [(0, 1, 77), (1, 1, 81), (2, 2, 84)], [(0, 1, 83), (1, 1, 79), (2, 2, 74)],
        [(0, 2, 79), (2, 1, 76), (3, 1, 79)], [(0, 2, 81), (2, 1, 79), (3, 1, 76)],
        [(0, 1, 77), (1, 1, 79), (2, 1, 81), (3, 1, 84)], [(0, 3, 83), (3, 1, None)]]
    for bar in range(8):
        root, tri = chords[bar]
        for k in range(8):                                    # arpège doux
            put(buf, (bar * 4 + k * 0.5) * beat,
                note("bell", root + 12 + tri[k % 3], beat * 1.2, 0.10, decay=3.0))
        put(buf, bar * 4 * beat, note("sine", root - 12, beat * 3.6, 0.22, decay=0.6))
        for b, d, m in melody[bar]:
            if m:
                put(buf, (bar * 4 + b) * beat, note("bell", m, d * beat * 1.4, 0.30, decay=2.2))
    return buf


def music_classic():
    """Aventure chiptune joyeuse (coucher de soleil)."""
    beat, buf = track(132, 8)
    roots = [48, 43, 45, 41] * 2
    chords = [(0, 4, 7), (0, 4, 7), (0, 3, 7), (0, 4, 7)] * 2
    lead = [[72, 76, 79, 76, 72, 76, 79, 76], [74, 79, 83, 79, 74, 79, 83, 79],
            [72, 76, 81, 76, 72, 76, 81, 79], [72, 77, 81, 77, 76, 77, 79, None],
            [79, None, 79, 81, 79, 76, 72, 76], [74, None, 74, 76, 79, 83, 79, 74],
            [81, 79, 76, 72, 76, 79, 81, 84], [84, 81, 77, 81, 79, None, 72, None]]
    for bar in range(8):
        r, tri = roots[bar], chords[bar]
        for k in range(8):
            t0 = (bar * 4 + k * 0.5) * beat
            put(buf, t0, note("tri", r + (12 if k % 4 == 2 else 0), beat * 0.45, 0.55, decay=2))
            m = lead[bar][k]
            if m:
                put(buf, t0, note("pulse", m, beat * 0.42, 0.17, decay=3))
            put(buf, t0 + 0.25 * beat, note("sine", r + 24 + tri[k % 3], beat * 0.2, 0.05))
            if k % 2 == 1:
                put(buf, t0, noise(0.04, 0.10, 60))          # charleston
        put(buf, bar * 4 * beat, sweep("sine", 150, 45, 0.18, 0.5, 18))          # grosse caisse
        put(buf, (bar * 4 + 2) * beat, sweep("sine", 150, 45, 0.18, 0.5, 18))
    return buf


def music_fantasy():
    """Forêt de minuit : mineur, mystérieux."""
    beat, buf = track(96, 8)
    roots = [45, 41, 48, 43] * 2
    tri_types = [(0, 3, 7), (0, 4, 7), (0, 4, 7), (0, 4, 7)] * 2
    melody = [[(0, 2, 81), (2, 1, 79), (3, 1, 76)], [(0, 2, 77), (2, 1, 76), (3, 1, 72)],
              [(0, 1.5, 76), (1.5, 0.5, 79), (2, 2, 84)], [(0, 2, 83), (2, 1, 79), (3, 1, 74)],
              [(0, 1, 81), (1, 1, 84), (2, 1, 88), (3, 1, 84)], [(0, 2, 84), (2, 1, 81), (3, 1, 77)],
              [(0, 1, 79), (1, 1, 76), (2, 1, 72), (3, 1, 76)], [(0, 2, 74), (2, 2, None)]]
    for bar in range(8):
        r, tri = roots[bar], tri_types[bar]
        put(buf, bar * 4 * beat, note("sine", r, beat * 3.9, 0.35, decay=0.3))       # basse
        for iv in tri:                                                              # nappe
            put(buf, bar * 4 * beat, note("tri", r + 12 + iv, beat * 3.9, 0.07, attack=0.4))
        for k in range(16):                                                         # arpège
            put(buf, (bar * 4 + k * 0.25) * beat,
                note("pulse", r + 24 + tri[(k % 4) if k % 4 < 3 else 1], beat * 0.22, 0.06, decay=6))
        for b, d, m in melody[bar]:
            if m:
                put(buf, (bar * 4 + b) * beat,
                    note("tri", m, d * beat * 0.95, 0.28, decay=0.8, vibrato=0.006))
        put(buf, bar * 4 * beat, sweep("sine", 90, 40, 0.3, 0.35, 8))
    return echo(buf, 0.31, 0.25, 2)


def music_space():
    """Espace : basses pulsées, arpèges brillants, écho."""
    beat, buf = track(118, 8)
    roots = [38, 34, 36, 33] * 2
    tri_types = [(0, 3, 7), (0, 4, 7), (0, 4, 7), (0, 4, 7)] * 2
    pattern = [0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1, 0, 1, 2, 1]
    lead = [[(0, 2, 74), (2, 2, 77)], [(0, 2, 74), (2, 2, 72)], [(0, 2, 76), (2, 2, 79)],
            [(0, 3, 77), (3, 1, 76)], [(0, 2, 81), (2, 2, 79)], [(0, 2, 77), (2, 2, 74)],
            [(0, 2, 79), (2, 2, 84)], [(0, 3, 81), (3, 1, None)]]
    for bar in range(8):
        r, tri = roots[bar], tri_types[bar]
        for k in range(8):                                                          # basse pulsée
            put(buf, (bar * 4 + k * 0.5) * beat,
                note("saw", r + (12 if k % 4 == 3 else 0), beat * 0.4, 0.30, decay=4))
        notes = [r + 36, r + 36 + tri[1], r + 36 + tri[2], r + 48]
        for k, idx in enumerate(pattern):                                           # arpège
            put(buf, (bar * 4 + k * 0.25) * beat,
                note("sine", notes[idx], beat * 0.3, 0.09, decay=7))
        for b, d, m in lead[bar]:
            if m:
                put(buf, (bar * 4 + b) * beat,
                    note("sine", m, d * beat * 0.95, 0.20, attack=0.05, vibrato=0.01))
        put(buf, bar * 4 * beat, sweep("sine", 120, 40, 0.25, 0.5, 10))
        put(buf, (bar * 4 + 2) * beat, noise(0.05, 0.12, 50))
    return echo(buf, 0.254, 0.4, 3)


# ---------------------------------------------------------------- effets
def sound_effects():
    save("shoot", sweep("square", 1100, 280, 0.11, 0.5, 14))
    save("jump", sweep("tri", 280, 760, 0.16, 0.6, 4))
    hit = np.zeros(int(0.08 * SR))
    put(hit, 0, noise(0.05, 0.6, 60))
    put(hit, 0, sweep("sine", 260, 120, 0.06, 0.5))
    save("hit", hit)
    kill = np.zeros(int(0.35 * SR))
    put(kill, 0, noise(0.30, 0.7, 12))
    put(kill, 0, sweep("saw", 420, 60, 0.32, 0.45, 8))
    save("kill", kill)
    stomp = np.zeros(int(0.22 * SR))
    put(stomp, 0, sweep("sine", 420, 90, 0.18, 0.8, 10))
    put(stomp, 0, noise(0.08, 0.35, 40))
    save("stomp", stomp)
    pick = np.zeros(int(0.35 * SR))
    for i, m in enumerate((72, 76, 79, 84)):
        put(pick, i * 0.06, note("square", m, 0.09, 0.4, decay=6))
    save("pickup", pick)
    hurt = np.zeros(int(0.3 * SR))
    put(hurt, 0, sweep("saw", 220, 70, 0.28, 0.6, 5))
    put(hurt, 0, noise(0.12, 0.35, 25))
    save("hurt", hurt)
    spawn = np.zeros(int(0.55 * SR))
    put(spawn, 0, sweep("saw", 95, 55, 0.5, 0.5, 3))
    put(spawn, 0, sweep("square", 47, 40, 0.5, 0.3, 3))
    save("spawn", spawn)
    win = np.zeros(int(1.6 * SR))
    for i, m in enumerate((72, 76, 79, 84)):
        put(win, i * 0.14, note("square", m, 0.16, 0.30, decay=3))
    for m in (72, 76, 79, 84):
        put(win, 0.62, note("tri", m, 0.9, 0.25, decay=2.5))
    save("win", win)
    lose = np.zeros(int(2.0 * SR))
    for i, m in enumerate((69, 65, 62, 57)):
        put(lose, i * 0.32, note("saw", m, 0.4, 0.28, decay=3))
    put(lose, 1.3, note("tri", 45, 0.7, 0.4, decay=2))
    save("lose", lose)


if __name__ == "__main__":
    save("music_menu", music_menu(), 0.8)
    save("music_classic", music_classic(), 0.8)
    save("music_fantasy", music_fantasy(), 0.8)
    save("music_space", music_space(), 0.8)
    sound_effects()