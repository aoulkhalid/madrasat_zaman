# -*- coding: utf-8 -*-
"""
games/investment_data.py — Le Bon Investissement
Chaque scénario : mise en situation + rendements cachés par poste
(inconnus des équipes pendant la répartition, révélés après validation).
"""

ALL_SCENARIOS = [
    {
        "title": "Startup SaaS qui vient de lever des fonds",
        "description": "Une jeune entreprise de logiciel en ligne doit accélérer sa croissance.",
        "multipliers": {"marketing": 1.4, "rnd": 0.9, "recrutement": 1.1, "dev": 1.6},
    },
    {
        "title": "E-commerce en pleine période de soldes",
        "description": "Un site de vente en ligne doit gérer un pic de trafic saisonnier.",
        "multipliers": {"marketing": 1.7, "rnd": 0.6, "recrutement": 0.8, "dev": 1.2},
    },
    {
        "title": "Entreprise industrielle en difficulté technique",
        "description": "Des pannes récurrentes menacent la production d'une usine.",
        "multipliers": {"marketing": 0.5, "rnd": 1.8, "recrutement": 0.9, "dev": 1.3},
    },
    {
        "title": "Startup en pleine explosion des inscriptions",
        "description": "Le produit fonctionne, mais l'équipe technique est débordée.",
        "multipliers": {"marketing": 0.6, "rnd": 1.0, "recrutement": 1.5, "dev": 1.7},
    },
    {
        "title": "Marque de mode qui cherche à se différencier",
        "description": "Le marché est saturé, il faut une identité forte pour émerger.",
        "multipliers": {"marketing": 1.8, "rnd": 1.3, "recrutement": 0.7, "dev": 0.6},
    },
    {
        "title": "Entreprise tech en pénurie de talents",
        "description": "Les concurrents recrutent agressivement les meilleurs profils.",
        "multipliers": {"marketing": 0.7, "rnd": 1.1, "recrutement": 1.8, "dev": 1.2},
    },
]