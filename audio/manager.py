"""audio/manager.py — Gestionnaire audio pygame"""
import os
from config import SOUNDS_DIR

TRACKS = {
    "calm":    "calm.wav",
    "tension": "tension.wav",
    "victory": "victory.wav",
}

class AudioManager:
    def __init__(self):
        self._ok      = False
        self._current = None
        self._muted   = False
        self._init()

    def _init(self):
        try:
            import pygame
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self._mixer = pygame.mixer
            self._ok    = True
        except Exception as e:
            print(f"[Audio] {e}")

    def play(self, track: str):
        if not self._ok or self._muted or track == self._current:
            return
        path = os.path.join(SOUNDS_DIR, TRACKS.get(track, ""))
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
        if not self._ok: return
        try:
            self._mixer.music.fadeout(600)
            self._current = None
        except: pass

    def toggle_mute(self) -> bool:
        self._muted = not self._muted
        if self._muted:
            self.stop()
        return self._muted

    def play_clip(self, path: str, volume: float = 0.7):
        """Joue un extrait one-shot (ex. jeu musical) sur un canal séparé,
        sans boucle, sans couper la musique d'ambiance en cours."""
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
        """Arrête un extrait lancé par play_clip()."""
        if channel:
            try:
                channel.stop()
            except Exception:
                pass

    @property
    def is_muted(self): return self._muted