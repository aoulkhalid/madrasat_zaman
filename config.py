"""
config.py — Madrasat Zaman v3
Constantes globales, palette, thème QSS, définition des équipes
"""
import os

# ── Chemins ───────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
LOGOS_DIR  = os.path.join(ASSETS_DIR, "images", "logos")
DIFF_DIR   = os.path.join(ASSETS_DIR, "images", "diff")

# ── App ───────────────────────────────────────────────────────────────────────
APP_TITLE   = "Madrasat Zaman | مدرسة زمان"
APP_VERSION = "3.0"

# ── Équipes ───────────────────────────────────────────────────────────────────
TEAMS = {
    "A": {"name": "Équipe A", "color": "#1a5c8a", "light": "#d6eaf8",
          "emoji": "🔵", "letter": "A"},
    "B": {"name": "Équipe B", "color": "#c0392b", "light": "#fadbd8",
          "emoji": "🔴", "letter": "B"},
    "C": {"name": "Équipe C", "color": "#17a589", "light": "#d1f2eb",
          "emoji": "🟢", "letter": "C"},
    "D": {"name": "Équipe D", "color": "#d35400", "light": "#fdebd0",
          "emoji": "🟠", "letter": "D"},
}

# ── Tournoi ───────────────────────────────────────────────────────────────────
TOURNAMENT_STRUCTURE = [
    {"id": 0, "label": "Demi-finale 1", "team1": "A", "team2": "B"},
    {"id": 1, "label": "Demi-finale 2", "team1": "C", "team2": "D"},
    {"id": 2, "label": "Finale",        "team1": None, "team2": None},  # TBD
]

# ── Jeu ───────────────────────────────────────────────────────────────────────
TIMER_DURATION  = 35
POINTS_CORRECT  = 5
POINTS_WRONG    = 0
QUIZ_PER_MATCH  = 20    # questions par match
LOGO_PER_MATCH  = 20    # logos par match
DIFF_PER_MATCH  = 10    # paires d'images par match

# ── Couleurs ─────────────────────────────────────────────────────────────────
C = {
    "bg":            "#e8f1f8",
    "bg_card":       "#f5f9fc",
    "white":         "#ffffff",
    "primary":       "#0d3b6e",
    "primary_mid":   "#1a5c8a",
    "primary_light": "#2980b9",
    "accent":        "#17a589",
    "success":       "#27ae60",
    "success_bg":    "#d5f5e3",
    "error":         "#e74c3c",
    "error_bg":      "#fadbd8",
    "warning":       "#f39c12",
    "text_dark":     "#1a2c42",
    "text_med":      "#2c3e50",
    "text_light":    "#7f8c8d",
    "border":        "#cde0ef",
    "shadow":        "#b2c5d6",
}

# ── QSS Thème global ──────────────────────────────────────────────────────────
QSS = f"""
* {{
    font-family: Arial, sans-serif;
}}
QMainWindow, QWidget {{
    background-color: {C['bg']};
}}
QFrame#card {{
    background-color: {C['white']};
    border-radius: 16px;
    border: 1px solid {C['border']};
}}
QFrame#header {{
    background-color: {C['primary']};
    min-height: 58px;
    max-height: 58px;
}}
QLabel#header_brand {{
    color: white;
    font-size: 13px;
    font-weight: bold;
}}
QLabel#section_lbl {{
    color: {C['text_light']};
    font-size: 13px;
}}
QPushButton#primary {{
    background-color: {C['primary']};
    color: white;
    border-radius: 12px;
    border: none;
    font-size: 14px;
    font-weight: bold;
    padding: 12px 28px;
    min-height: 44px;
}}
QPushButton#primary:hover {{
    background-color: {C['primary_mid']};
}}
QPushButton#primary:pressed {{
    background-color: #0a2d52;
}}
QPushButton#primary:disabled {{
    background-color: {C['text_light']};
}}
QPushButton#secondary {{
    background-color: {C['white']};
    color: {C['primary']};
    border-radius: 12px;
    border: 2px solid {C['border']};
    font-size: 13px;
    font-weight: bold;
    padding: 10px 20px;
    min-height: 40px;
}}
QPushButton#secondary:hover {{
    background-color: {C['bg']};
    border-color: {C['primary_mid']};
}}
QPushButton#success_btn {{
    background-color: {C['success']};
    color: white;
    border-radius: 12px;
    border: none;
    font-size: 16px;
    font-weight: bold;
    padding: 14px 28px;
    min-height: 50px;
}}
QPushButton#success_btn:hover {{
    background-color: #219a52;
}}
QPushButton#danger_btn {{
    background-color: {C['error']};
    color: white;
    border-radius: 12px;
    border: none;
    font-size: 16px;
    font-weight: bold;
    padding: 14px 28px;
    min-height: 50px;
}}
QPushButton#danger_btn:hover {{
    background-color: #a93226;
}}
QPushButton#answer_btn {{
    background-color: {C['white']};
    color: {C['text_dark']};
    border-radius: 10px;
    border: 2px solid {C['border']};
    font-size: 13px;
    padding: 10px 14px;
    text-align: left;
    min-height: 48px;
}}
QPushButton#answer_btn:hover:enabled {{
    background-color: #edf4fb;
    border-color: {C['primary_light']};
}}
QPushButton#answer_btn:disabled {{
    color: {C['text_light']};
}}
QPushButton#back_btn {{
    background-color: transparent;
    color: white;
    border: none;
    font-size: 22px;
    font-weight: bold;
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
    border-radius: 8px;
}}
QPushButton#back_btn:hover {{
    background-color: rgba(255,255,255,30);
}}
QPushButton#audio_btn {{
    background-color: rgba(255,255,255,20);
    color: white;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,40);
    font-size: 18px;
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
}}
QPushButton#audio_btn:hover {{
    background-color: rgba(255,255,255,40);
}}
QLineEdit {{
    background-color: {C['bg_card']};
    border: 2px solid {C['border']};
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13px;
    color: {C['text_dark']};
}}
QLineEdit:focus {{
    border-color: {C['primary_light']};
}}
QFrame#score_box {{
    background-color: {C['white']};
    border-radius: 10px;
    border: 1px solid {C['border']};
    min-width: 100px;
    max-width: 110px;
    min-height: 62px;
    max-height: 62px;
}}
QFrame#team_banner {{
    min-height: 44px;
    max-height: 44px;
}}
QProgressBar {{
    background-color: {C['border']};
    border: none;
    border-radius: 4px;
    max-height: 8px;
}}
QProgressBar::chunk {{
    background-color: {C['primary']};
    border-radius: 4px;
}}
"""
