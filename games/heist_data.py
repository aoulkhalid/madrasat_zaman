# -*- coding: utf-8 -*-
"""
games/heist_data.py — Braquage de Banque

40 questions au total :
    - 20 questions pour l'équipe A
    - 20 questions pour l'équipe B

Organisation :
    Clé 1 : questions 1 → 5
    Clé 2 : questions 6 → 10
    Clé 3 : questions 11 → 15
    Clé 4 : questions 16 → 20

Chaque bonne réponse = +5 points.
Si une équipe réussit les 20 questions :
    +10 points bonus = Banque braquée.
"""

ALL_MISSIONS = [

    # ============================================================
    # ======================== ÉQUIPE A ==========================
    # ============================================================

    # 🔑 CLÉ 1 — Questions 1 à 5
    {
        "icon": "🧮",
        "title": "Calcul",
        "question": "Résolvez : 3 × 7 + 5 = ?",
        "answer": "26"
    },
    {
        "icon": "🧠",
        "title": "Logique",
        "question": "Un nombre est multiplié par 2 puis on ajoute 6. Le résultat est 20. Quel est le nombre ?",
        "answer": "7"
    },
    {
        "icon": "💻",
        "title": "Informatique",
        "question": "Que signifie CPU ?",
        "answer": "Central Processing Unit"
    },
    {
        "icon": "🌍",
        "title": "Culture générale",
        "question": "Quelle est la capitale de l'Australie ?",
        "answer": "Canberra"
    },
    {
        "icon": "🔬",
        "title": "Science",
        "question": "Quelle planète est surnommée la planète rouge ?",
        "answer": "Mars"
    },

    # 🔑 CLÉ 2 — Questions 6 à 10
    {
        "icon": "🧮",
        "title": "Mathématiques",
        "question": "Résolvez : 2X + 8 = 20. Quelle est la valeur de X ?",
        "answer": "6"
    },
    {
        "icon": "🐍",
        "title": "Programmation",
        "question": "Quel langage de programmation utilise le symbole 🐍 comme mascotte ?",
        "answer": "Python"
    },
    {
        "icon": "⚡",
        "title": "Physique",
        "question": "Quelle est l'unité de mesure de la force dans le système international ?",
        "answer": "Newton"
    },
    {
        "icon": "🧬",
        "title": "Biologie",
        "question": "Quelle molécule contient principalement l'information génétique ?",
        "answer": "ADN"
    },
    {
        "icon": "🌐",
        "title": "Web",
        "question": "Que signifie HTML ?",
        "answer": "HyperText Markup Language"
    },

    # 🔑 CLÉ 3 — Questions 11 à 15
    {
        "icon": "🧠",
        "title": "Logique",
        "question": "Si tous les A sont des B et que tous les B sont des C, les A sont-ils forcément des C ?",
        "answer": "Oui"
    },
    {
        "icon": "💻",
        "title": "Algorithmique",
        "question": "Quelle est la complexité d'une recherche dichotomique dans un tableau trié ?",
        "answer": "O(log n)"
    },
    {
        "icon": "📊",
        "title": "Data",
        "question": "Quelle mesure statistique indique la valeur située au milieu d'une série ordonnée ?",
        "answer": "Médiane"
    },
    {
        "icon": "🤖",
        "title": "Intelligence artificielle",
        "question": "Quel type d'apprentissage utilise des données avec des réponses déjà connues ?",
        "answer": "Apprentissage supervisé"
    },
    {
        "icon": "🔐",
        "title": "Cybersécurité",
        "question": "Comment appelle-t-on une tentative de tromper une personne pour voler ses informations personnelles par message ou email ?",
        "answer": "Phishing"
    },

    # 🔑 CLÉ 4 — Questions 16 à 20
    {
        "icon": "🧮",
        "title": "Mathématiques",
        "question": "Si x² = 49, quelles sont les valeurs possibles de x ?",
        "answer": "7 et -7"
    },
    {
        "icon": "💻",
        "title": "Programmation",
        "question": "Quelle est la différence principale entre une variable locale et une variable globale ?",
        "answer": "La portée"
    },
    {
        "icon": "🤖",
        "title": "Machine Learning",
        "question": "À quoi sert principalement la normalisation des données avant certains algorithmes de machine learning ?",
        "answer": "Mettre les variables sur une échelle comparable"
    },
    {
        "icon": "🌐",
        "title": "Réseaux",
        "question": "Quel protocole est principalement utilisé pour sécuriser la navigation web avec HTTPS ?",
        "answer": "TLS"
    },
    {
        "icon": "🧠",
        "title": "Algorithmique",
        "question": "Quelle structure de données fonctionne selon le principe LIFO ?",
        "answer": "Pile / Stack"
    },

    # ============================================================
    # ======================== ÉQUIPE B ==========================
    # ============================================================

    # 🔑 CLÉ 1 — Questions 1 à 5
    {
        "icon": "🧮",
        "title": "Calcul",
        "question": "Résolvez : 5 × 6 - 8 = ?",
        "answer": "22"
    },
    {
        "icon": "🧠",
        "title": "Logique",
        "question": "Un père a 4 filles. Chaque fille a un frère. Combien d'enfants a le père ?",
        "answer": "5"
    },
    {
        "icon": "💻",
        "title": "Informatique",
        "question": "Que signifie RAM ?",
        "answer": "Random Access Memory"
    },
    {
        "icon": "🌍",
        "title": "Géographie",
        "question": "Quel est le plus grand océan du monde ?",
        "answer": "Océan Pacifique"
    },
    {
        "icon": "🔬",
        "title": "Science",
        "question": "Quel gaz les humains respirent-ils principalement pour vivre ?",
        "answer": "Oxygène"
    },

    # 🔑 CLÉ 2 — Questions 6 à 10
    {
        "icon": "🧮",
        "title": "Mathématiques",
        "question": "Résolvez : 3X - 5 = 16. Quelle est la valeur de X ?",
        "answer": "7"
    },
    {
        "icon": "🌐",
        "title": "Web",
        "question": "Quel langage est principalement utilisé pour styliser une page web ?",
        "answer": "CSS"
    },
    {
        "icon": "⚡",
        "title": "Physique",
        "question": "Quelle est l'unité de mesure de la puissance électrique ?",
        "answer": "Watt"
    },
    {
        "icon": "🧬",
        "title": "Biologie",
        "question": "Quel organe pompe le sang dans le corps humain ?",
        "answer": "Cœur"
    },
    {
        "icon": "🐧",
        "title": "Système",
        "question": "Quel système d'exploitation utilise le noyau Linux ?",
        "answer": "Linux"
    },

    # 🔑 CLÉ 3 — Questions 11 à 15
    {
        "icon": "🧠",
        "title": "Logique",
        "question": "Tu participes à une course et tu dépasses le deuxième. Quelle est ta position ?",
        "answer": "Deuxième"
    },
    {
        "icon": "💻",
        "title": "Algorithmique",
        "question": "Quelle structure de données fonctionne selon le principe FIFO ?",
        "answer": "File / Queue"
    },
    {
        "icon": "📊",
        "title": "Statistiques",
        "question": "Quelle mesure statistique correspond à la moyenne de plusieurs valeurs ?",
        "answer": "Moyenne"
    },
    {
        "icon": "🤖",
        "title": "Intelligence artificielle",
        "question": "Quel type d'apprentissage permet à un agent d'apprendre grâce aux récompenses et aux pénalités ?",
        "answer": "Apprentissage par renforcement"
    },
    {
        "icon": "🔐",
        "title": "Cybersécurité",
        "question": "Que signifie MFA en cybersécurité ?",
        "answer": "Multi-Factor Authentication"
    },

    # 🔑 CLÉ 4 — Questions 16 à 20
    {
        "icon": "🧮",
        "title": "Mathématiques",
        "question": "Quelle est la dérivée de x² ?",
        "answer": "2x"
    },
    {
        "icon": "💻",
        "title": "Programmation",
        "question": "Quelle est la complexité moyenne d'une recherche dans une table de hachage bien conçue ?",
        "answer": "O(1)"
    },
    {
        "icon": "🤖",
        "title": "Machine Learning",
        "question": "Quelle différence principale existe entre classification et régression ?",
        "answer": "Classification prédit des catégories, régression prédit une valeur"
    },
    {
        "icon": "🌐",
        "title": "Réseaux",
        "question": "Quel protocole est généralement utilisé pour transférer des pages web ?",
        "answer": "HTTP"
    },
    {
        "icon": "🧠",
        "title": "Algorithmique",
        "question": "Quelle technique permet de diviser un problème en sous-problèmes puis de combiner leurs solutions ?",
        "answer": "Diviser pour régner"
    },
]