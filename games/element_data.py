# -*- coding: utf-8 -*-
"""
games/element_data.py — Jeu des Éléments
Chaque entrée : deux éléments combinés + 4 choix de réponse (1 correcte)
"""

ALL_COMBOS = [
    {"a": "🔥 Feu", "b": "💧 Eau", "answer": 0,
     "choices": ["💨 Vapeur", "🪨 Pierre", "❄️ Glace", "🌪 Tornade"]},

    {"a": "🔥 Feu", "b": "🌍 Terre", "answer": 1,
     "choices": ["💨 Vapeur", "🌋 Lave", "🌧 Pluie", "❄️ Glace"]},

    {"a": "🔥 Feu", "b": "🌪 Vent", "answer": 2,
     "choices": ["🌧 Pluie", "🪨 Pierre", "💥 Explosion", "🧊 Glaçon"]},

    {"a": "💧 Eau", "b": "🌍 Terre", "answer": 3,
     "choices": ["💨 Vapeur", "💥 Explosion", "☁️ Nuage", "🟤 Boue"]},

    {"a": "💧 Eau", "b": "🌪 Vent", "answer": 0,
     "choices": ["🌧 Pluie / Brouillard", "🌋 Lave", "🟤 Boue", "💥 Explosion"]},

    {"a": "🌍 Terre", "b": "🌪 Vent", "answer": 2,
     "choices": ["🌧 Pluie", "🌋 Lave", "🏜 Tempête de sable", "☁️ Nuage"]},

    {"a": "💧 Eau", "b": "🔥 Feu", "answer": 0,
     "choices": ["💨 Vapeur", "🟤 Boue", "🏜 Sable", "❄️ Glace"]},

    {"a": "🌪 Vent", "b": "🔥 Feu", "answer": 3,
     "choices": ["🌧 Pluie", "🟤 Boue", "☁️ Nuage", "💥 Explosion / Feu ravageur"]},

    {"a": "🌍 Terre", "b": "🔥 Feu", "answer": 1,
     "choices": ["💨 Vapeur", "🌋 Lave / Volcan", "🌧 Pluie", "🧊 Glaçon"]},

    {"a": "🌪 Vent", "b": "🌍 Terre", "answer": 2,
     "choices": ["☁️ Nuage", "🌋 Lave", "🏜 Poussière / Tempête de sable", "🟤 Boue"]},

    {"a": "🌪 Vent", "b": "💧 Eau", "answer": 0,
     "choices": ["🌫 Brouillard", "🌋 Lave", "🏜 Sable", "🔥 Braise"]},

    {"a": "🌍 Terre", "b": "💧 Eau", "answer": 3,
     "choices": ["☁️ Nuage", "🌋 Lave", "💨 Vapeur", "🟤 Boue / Argile"]},
]