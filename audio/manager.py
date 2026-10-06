"""audio/manager.py — Gestionnaire audio pygame

Musique d'ambiance : SEULEMENT home/menu (calm) et result (victory).
Dans les jeux : silence, sauf le "tak" chaque seconde et le "tit" à 0.
"""
import os
from config import SOUNDS_DIR

TRACKS = {
    "calm":    "calm.wav",
    "victory": "victory.wav",
}

# Effets courts : nom -> (fichier, volume)
SFX = {
    "tick": ("tick.wav", 0.5),   # "tak" chaque seconde
    "beep": ("beep.wav", 1.0),   # "tit" à 0
}


class AudioManager:
    def __init__(self):
        self._ok      = False
        self._current = None   # track en cours de lecture
        self._wanted  = None   # track qui devrait jouer (pour mute/unmute)
        self._muted   = False
        self._sfx     = {}
        self._init()

    def _init(self):
        try:
            import pygame
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self._mixer = pygame.mixer
            self._mixer.set_num_channels(16)
            self._ok    = True
        except Exception as e:
            print(f"[Audio] init error: {e}")
            return
        self._load_sfx()

    def _load_sfx(self):
        """Charge les effets sonores une seule fois au démarrage."""
        for name, (fname, vol) in SFX.items():
            path = os.path.join(SOUNDS_DIR, fname)
            if not os.path.exists(path):
                print(f"[Audio] fichier introuvable : {path}")
                continue
            try:
                snd = self._mixer.Sound(path)
                snd.set_volume(vol)
                self._sfx[name] = snd
            except Exception as e:
                print(f"[Audio] erreur chargement {fname}: {e}")

    def _play_sfx(self, name: str):
        if not self._ok or self._muted:
            return
        snd = self._sfx.get(name)
        if snd is None:
            return
        try:
            snd.play()
        except Exception as e:
            print(f"[Audio] sfx error ({name}): {e}")

    def play_tick(self):
        """'tak' : chaque seconde du chrono."""
        self._play_sfx("tick")

    def play_beep(self):
        """'tit' : quand le chrono arrive à 0."""
        self._play_sfx("beep")

    # ── Musique d'ambiance ────────────────────────────────────────

    def play(self, track: str):
        # Tout track inconnu (ex. "tension") est ignoré
        if track not in TRACKS:
            return
        self._wanted = track
        if not self._ok or self._muted or track == self._current:
            return
        path = os.path.join(SOUNDS_DIR, TRACKS[track])
        if not os.path.exists(path):
            return
        try:
            self._mixer.music.load(path)
            self._mixer.music.set_volume(0.35)
            self._mixer.music.play(loops=-1, fade_ms=800)
            self._current = track
        except Exception as e:
            print(f"[Audio] play error: {e}")

    def stop(self):
        self._wanted = None
        if not self._ok:
            return
        try:
            # stop() et non fadeout() : fadeout() bloque l'interface
            self._mixer.music.stop()
            self._current = None
        except Exception:
            pass

    def resume_ambient(self):
        """Relance l'ambiance si elle doit jouer (home/menu/result)."""
        if not self._ok or self._muted:
            return
        if self._wanted and self._wanted != self._current:
            self.play(self._wanted)

    def toggle_mute(self) -> bool:
        self._muted = not self._muted
        if self._muted:
            wanted = self._wanted
            self.stop()
            self._wanted = wanted
        else:
            self.resume_ambient()
        return self._muted

    # ── Extraits (blind test) ─────────────────────────────────────

    def play_clip(self, path: str, volume: float = 0.7):
        """Extrait one-shot (blind test), sans toucher à l'ambiance."""
        if not self._ok or self._muted:
            return None
        try:
            sound = self._mixer.Sound(path)
            sound.set_volume(volume)
            return sound.play()
        except Exception as e:
            print(f"[Audio] play_clip error: {e}")
            return None

    def stop_clip(self, channel):
        if channel:
            try:
                channel.stop()
            except Exception:
                pass

    @property
    def is_muted(self):
        return self._muted