# -*- coding: utf-8 -*-
"""
games/cyber_data.py — Cyber Investigation
Madrasat Zaman v3

UNE SEULE HISTOIRE, 8 INDICES, DANS L'ORDRE.
(Doit rester à 8 : la page affiche toujours les 8 indices, dans cet ordre.)

Scénario — entreprise "Atlas", cette nuit :

  21:58  un faux e-mail arrive à l'employé (compte support@atlas.local)
  22:03  il clique sur le lien
  22:04  il saisit ses identifiants sur la fausse page
  22:14  l'attaquant se connecte au serveur avec ce compte
  22:17  il ouvre le dossier /confidential/
  22:19  il crée l'archive backup_temp.zip (184 MB)
  22:21  l'archive part vers l'extérieur (184 MB)

Fil conducteur : la MÊME adresse IP, 185.72.44.19, revient dans
la connexion, le faux lien et le transfert — c'est elle qui relie tout.

Chaque indice : icon, title, clue (la situation), question, answer.
"""

ALL_CLUES = [

    # ── 1 ── Les journaux : quelle IP est suspecte ? ───────────────────────────
    {
        "icon": "🚨",
        "title": "Alerte de sécurité",
        "clue": (
            "Le serveur interne d'Atlas a déclenché une alerte cette nuit.\n"
            "Voici les connexions enregistrées :\n\n"
            "21:40 — IP 10.0.0.12 — connexion réussie\n"
            "22:05 — IP 10.0.0.47 — connexion réussie\n"
            "22:14 — IP 185.72.44.19 — réussie après 2 échecs\n\n"
            "Les adresses 10.0.0.x sont celles du bureau de l'entreprise."
        ),
        "question": "Quelle adresse IP est suspecte ?",
        "answer": "185.72.44.19 (seule IP extérieure, connexion réussie après 2 échecs)",
    },

    # ── 2 ── Le compte utilisé ─────────────────────────────────────────────────
    {
        "icon": "👤",
        "title": "Le compte utilisé",
        "clue": (
            "Les enquêteurs filtrent le journal sur l'adresse 185.72.44.19 :\n\n"
            "22:14:03 — support@atlas.local — échec (mot de passe)\n"
            "22:14:09 — support@atlas.local — échec (mot de passe)\n"
            "22:14:15 — support@atlas.local — connexion réussie\n\n"
            "L'attaquant a donc essayé de se connecter avec un compte précis."
        ),
        "question": "Quel compte l'attaquant a-t-il utilisé ?",
        "answer": "support@atlas.local",
    },

    # ── 3 ── Le mail piégé ─────────────────────────────────────────────────────
    {
        "icon": "📧",
        "title": "Le message reçu",
        "clue": (
            "Dans la boîte mail de support@atlas.local, un message est arrivé "
            "à 21:58, avant l'intrusion :\n\n"
            "De : it-support@atlas-secure.com\n"
            "Objet : Votre compte sera bloqué\n\n"
            "« Cliquez sur ce lien pour confirmer votre mot de passe. »\n\n"
            "Le domaine officiel de l'entreprise est : atlas.local"
        ),
        "question": "Quel type d'attaque ce message utilise-t-il ?",
        "answer": "Le phishing (hameçonnage)",
    },

    # ── 4 ── Le lien : il pointe vers la même IP ───────────────────────────────
    {
        "icon": "🔗",
        "title": "Le lien du message",
        "clue": (
            "L'employé a cliqué sur le lien à 22:03.\n\n"
            "Le lien affichait :  https://portal.atlas.local/login\n"
            "Sa vraie destination :  http://185.72.44.19/secure-login\n\n"
            "Cette page imitait le portail de connexion de l'entreprise."
        ),
        "question": "Quel élément relie ce lien à l'intrusion ?",
        "answer": "La même adresse IP : 185.72.44.19",
    },

    # ── 5 ── Les fichiers ciblés ───────────────────────────────────────────────
    {
        "icon": "📁",
        "title": "Les fichiers consultés",
        "clue": (
            "À 22:04, l'employé a saisi son mot de passe sur la fausse page. "
            "À 22:14, l'attaquant s'est connecté avec ce même compte.\n\n"
            "Puis, entre 22:17 et 22:18, le compte support a ouvert :\n\n"
            "/confidential/clients_2026.xlsx\n"
            "/confidential/contrats.pdf\n"
            "/confidential/finances_Q3.xlsx\n\n"
            "Ce compte n'a normalement aucune raison d'aller là."
        ),
        "question": "Quel dossier l'attaquant a-t-il visé ?",
        "answer": "/confidential/",
    },

    # ── 6 ── L'archive ─────────────────────────────────────────────────────────
    {
        "icon": "💾",
        "title": "Un fichier apparaît",
        "clue": (
            "À 22:19, un nouveau fichier est créé par le compte support :\n\n"
            "backup_temp.zip — 184 MB\n\n"
            "Il contient exactement les trois fichiers du dossier /confidential/ "
            "consultés quelques minutes plus tôt."
        ),
        "question": "Pourquoi l'attaquant a-t-il créé cette archive ?",
        "answer": "Pour regrouper les données avant de les envoyer",
    },

    # ── 7 ── Le transfert ──────────────────────────────────────────────────────
    {
        "icon": "📤",
        "title": "Le pare-feu réagit",
        "clue": (
            "Le pare-feu a enregistré une connexion sortante :\n\n"
            "22:21 — destination 185.72.44.19\n"
            "Volume transféré : 184 MB\n\n"
            "C'est exactement la taille de backup_temp.zip."
        ),
        "question": "Que s'est-il passé à 22:21 ?",
        "answer": "Les données ont été volées (envoyées vers 185.72.44.19)",
    },

    # ── 8 ── La reconstitution ─────────────────────────────────────────────────
    {
        "icon": "🕒",
        "title": "La chronologie complète",
        "clue": (
            "Les enquêteurs reconstituent la nuit :\n\n"
            "21:58 — e-mail frauduleux reçu\n"
            "22:03 — clic sur le lien\n"
            "22:04 — mot de passe saisi sur la fausse page\n"
            "22:14 — connexion au serveur avec le compte support\n"
            "22:17 — accès au dossier /confidential/\n"
            "22:19 — création de backup_temp.zip\n"
            "22:21 — transfert de 184 MB vers 185.72.44.19"
        ),
        "question": "Quelle est la cause de toute l'attaque ?",
        "answer": "Le phishing : le faux e-mail a permis de voler le mot de passe",
    },
]

assert len(ALL_CLUES) == 8, "cyber_data : il doit y avoir exactement 8 indices"