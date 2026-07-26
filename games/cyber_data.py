# -*- coding: utf-8 -*-
"""
games/cyber_data.py — Cyber Investigation (version 1 PC, sans téléphones)
Chaque indice : icône, titre, mise en situation, question, réponse (révélée après validation)
"""

ALL_CLUES = [
    {"icon": "🖥️", "title": "Analyste des logs",
     "clue": "Connexion 1 — 192.168.1.25 — 14:20\nConnexion 2 — 192.168.1.56 — 14:32\nConnexion 3 — 192.168.1.18 — 14:45",
     "question": "À quelle heure exacte a eu lieu l'attaque ?", "answer": "14:32"},

    {"icon": "🌐", "title": "Traçage réseau",
     "clue": "Une des trois connexions ci-dessus est suspecte : elle a eu lieu pile au moment de l'intrusion.",
     "question": "Quelle adresse IP correspond à l'attaque ?", "answer": "192.168.1.56"},

    {"icon": "🔑", "title": "Expert mots de passe",
     "clue": "Le mot de passe volé est le nom d'un langage de programmation.",
     "question": "Complétez : P _ T H O N", "answer": "PYTHON"},

    {"icon": "🕵️", "title": "Profil du pirate",
     "clue": "Le pirate a laissé une signature dans les logs : un pseudonyme lié à l'ombre et au code.",
     "question": "Quel pseudonyme le pirate a-t-il utilisé ?", "answer": "ShadowByte (ou équivalent imaginé par l'équipe)"},

    {"icon": "🖥️", "title": "Analyste des logs",
     "clue": "Connexion 1 — 10.0.0.12 — 09:05\nConnexion 2 — 10.0.0.47 — 09:18\nConnexion 3 — 10.0.0.9 — 09:40",
     "question": "À quelle heure exacte a eu lieu l'attaque ?", "answer": "09:18"},

    {"icon": "🌐", "title": "Traçage réseau",
     "clue": "La connexion suspecte correspond à l'heure trouvée précédemment.",
     "question": "Quelle adresse IP correspond à l'attaque ?", "answer": "10.0.0.47"},

    {"icon": "🔑", "title": "Expert mots de passe",
     "clue": "Le mot de passe volé est le nom d'un langage utilisé pour le web.",
     "question": "Complétez : J _ V _ S C R I P T", "answer": "JAVASCRIPT"},

    {"icon": "🕵️", "title": "Profil du pirate",
     "clue": "Le pirate signe ses intrusions d'un nom inspiré d'un animal nocturne.",
     "question": "Quel pseudonyme le pirate a-t-il utilisé ?", "answer": "NightOwl (ou équivalent imaginé par l'équipe)"},

    {"icon": "🖥️", "title": "Analyste des logs",
     "clue": "Connexion 1 — 172.16.0.5 — 21:02\nConnexion 2 — 172.16.0.33 — 21:15\nConnexion 3 — 172.16.0.8 — 21:40",
     "question": "À quelle heure exacte a eu lieu l'attaque ?", "answer": "21:15"},

    {"icon": "🌐", "title": "Traçage réseau",
     "clue": "La connexion suspecte a eu lieu tard dans la soirée, à l'heure trouvée précédemment.",
     "question": "Quelle adresse IP correspond à l'attaque ?", "answer": "172.16.0.33"},

    {"icon": "🔑", "title": "Expert mots de passe",
     "clue": "Le mot de passe volé est le nom d'un langage utilisé pour l'intelligence artificielle et la data.",
     "question": "Complétez : R _ P Y T H O N (indice : un seul mot)", "answer": "PYTHON"},

    {"icon": "🕵️", "title": "Profil du pirate",
     "clue": "Le pirate signe ses intrusions d'un nom lié à la vitesse et à l'électricité.",
     "question": "Quel pseudonyme le pirate a-t-il utilisé ?", "answer": "FlashByte (ou équivalent imaginé par l'équipe)"},

    {"icon": "🖥️", "title": "Analyste des logs",
     "clue": "Connexion 1 — 10.10.1.4 — 03:12\nConnexion 2 — 10.10.1.19 — 03:47\nConnexion 3 — 10.10.1.2 — 04:05",
     "question": "À quelle heure exacte a eu lieu l'attaque ?", "answer": "03:47"},

    {"icon": "🌐", "title": "Traçage réseau",
     "clue": "L'intrusion a eu lieu en pleine nuit, à l'heure trouvée précédemment.",
     "question": "Quelle adresse IP correspond à l'attaque ?", "answer": "10.10.1.19"},

    {"icon": "🔑", "title": "Expert mots de passe",
     "clue": "Le mot de passe volé est le nom d'un système d'exploitation open source.",
     "question": "Complétez : L _ N U X", "answer": "LINUX"},

    {"icon": "🕵️", "title": "Profil du pirate",
     "clue": "Le pirate signe ses intrusions d'un nom lié à un fantôme numérique.",
     "question": "Quel pseudonyme le pirate a-t-il utilisé ?", "answer": "GhostProtocol (ou équivalent imaginé par l'équipe)"},
]