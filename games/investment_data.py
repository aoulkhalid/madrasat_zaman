# -*- coding: utf-8 -*-
"""
games/investment_data.py — Le Bon Investissement

Simulation business réaliste.

Chaque scénario contient :
- une situation d'entreprise
- des effets cachés liés aux investissements
- des effets sur :
    trésorerie
    clients
    réputation
    santé
    croissance

Les équipes ne connaissent pas les effets exacts avant de valider.
"""

ALL_SCENARIOS = [

    {
        "title": "🍔 Restaurant récemment ouvert",
        "description": (
            "Votre restaurant vient d'ouvrir. "
            "Les clients connaissent encore peu votre établissement "
            "et la concurrence est forte."
        ),

        "initial": {
            "cash": 100000,
            "clients": 500,
            "reputation": 50,
            "health": 75,
            "growth": 0,
        },

        "effects": {
            "marketing": {
                "cash": -1.00,
                "clients": 3.5,
                "reputation": 0.08,
                "health": -0.03,
                "growth": 0.04,
            },
            "rnd": {
                "cash": -1.00,
                "clients": 0.8,
                "reputation": 0.03,
                "health": 0.05,
                "growth": 0.08,
            },
            "recrutement": {
                "cash": -1.00,
                "clients": 1.5,
                "reputation": 0.05,
                "health": 0.12,
                "growth": 0.06,
            },
            "dev": {
                "cash": -1.00,
                "clients": 2.0,
                "reputation": 0.04,
                "health": 0.08,
                "growth": 0.10,
            },
        },

        "event": {
            "title": "🔥 Un concurrent ouvre juste à côté",
            "description": (
                "Un nouveau restaurant concurrent ouvre dans la même rue "
                "et attire une partie des clients."
            ),
            "effects": {
                "clients": -80,
                "reputation": -3,
                "health": -5,
                "growth": -4,
            }
        }
    },

    {
        "title": "💻 Startup SaaS en croissance",
        "description": (
            "Votre startup SaaS vient de lancer son produit. "
            "Les inscriptions augmentent rapidement mais votre équipe "
            "commence à être sous pression."
        ),

        "initial": {
            "cash": 100000,
            "clients": 800,
            "reputation": 65,
            "health": 70,
            "growth": 5,
        },

        "effects": {
            "marketing": {
                "cash": -1.00,
                "clients": 4.0,
                "reputation": 0.10,
                "health": -0.05,
                "growth": 0.08,
            },
            "rnd": {
                "cash": -1.00,
                "clients": 1.5,
                "reputation": 0.08,
                "health": 0.04,
                "growth": 0.16,
            },
            "recrutement": {
                "cash": -1.00,
                "clients": 2.0,
                "reputation": 0.06,
                "health": 0.15,
                "growth": 0.12,
            },
            "dev": {
                "cash": -1.00,
                "clients": 3.0,
                "reputation": 0.08,
                "health": 0.10,
                "growth": 0.18,
            },
        },

        "event": {
            "title": "🚨 Surcharge des serveurs",
            "description": (
                "Le nombre d'utilisateurs augmente brutalement. "
                "Les serveurs commencent à ralentir."
            ),
            "effects": {
                "clients": -100,
                "reputation": -8,
                "health": -6,
                "growth": -5,
            }
        }
    },

    {
        "title": "🛒 E-commerce pendant les soldes",
        "description": (
            "Votre boutique en ligne entre dans une période de soldes. "
            "Vous pouvez attirer beaucoup de nouveaux clients, "
            "mais votre plateforme doit supporter le trafic."
        ),

        "initial": {
            "cash": 100000,
            "clients": 1200,
            "reputation": 60,
            "health": 72,
            "growth": 8,
        },

        "effects": {
            "marketing": {
                "cash": -1.00,
                "clients": 5.0,
                "reputation": 0.10,
                "health": -0.06,
                "growth": 0.10,
            },
            "rnd": {
                "cash": -1.00,
                "clients": 1.0,
                "reputation": 0.06,
                "health": 0.04,
                "growth": 0.12,
            },
            "recrutement": {
                "cash": -1.00,
                "clients": 2.5,
                "reputation": 0.08,
                "health": 0.14,
                "growth": 0.08,
            },
            "dev": {
                "cash": -1.00,
                "clients": 4.0,
                "reputation": 0.10,
                "health": 0.12,
                "growth": 0.15,
            },
        },

        "event": {
            "title": "📈 Votre publicité devient virale !",
            "description": (
                "Une publication de votre marque devient virale "
                "et attire énormément de visiteurs."
            ),
            "effects": {
                "clients": 180,
                "reputation": 6,
                "health": -3,
                "growth": 8,
            }
        }
    },

    {
        "title": "🏭 Usine avec des problèmes techniques",
        "description": (
            "Votre usine connaît plusieurs pannes. "
            "La production ralentit et les clients commencent à se plaindre."
        ),

        "initial": {
            "cash": 100000,
            "clients": 900,
            "reputation": 55,
            "health": 60,
            "growth": -2,
        },

        "effects": {
            "marketing": {
                "cash": -1.00,
                "clients": 2.0,
                "reputation": 0.08,
                "health": -0.08,
                "growth": 0.02,
            },
            "rnd": {
                "cash": -1.00,
                "clients": 1.0,
                "reputation": 0.10,
                "health": 0.22,
                "growth": 0.15,
            },
            "recrutement": {
                "cash": -1.00,
                "clients": 1.5,
                "reputation": 0.06,
                "health": 0.15,
                "growth": 0.08,
            },
            "dev": {
                "cash": -1.00,
                "clients": 1.5,
                "reputation": 0.08,
                "health": 0.18,
                "growth": 0.12,
            },
        },

        "event": {
            "title": "⚙️ Nouvelle panne de production",
            "description": (
                "Une panne importante bloque une partie de la production "
                "pendant plusieurs heures."
            ),
            "effects": {
                "clients": -120,
                "reputation": -10,
                "health": -12,
                "growth": -6,
            }
        }
    },

    {
        "title": "👕 Marque de mode en difficulté",
        "description": (
            "Votre marque possède de bons produits mais reste inconnue. "
            "Vous devez choisir entre visibilité, innovation et équipe."
        ),

        "initial": {
            "cash": 100000,
            "clients": 700,
            "reputation": 45,
            "health": 68,
            "growth": 2,
        },

        "effects": {
            "marketing": {
                "cash": -1.00,
                "clients": 4.5,
                "reputation": 0.15,
                "health": -0.04,
                "growth": 0.12,
            },
            "rnd": {
                "cash": -1.00,
                "clients": 1.2,
                "reputation": 0.10,
                "health": 0.04,
                "growth": 0.15,
            },
            "recrutement": {
                "cash": -1.00,
                "clients": 1.5,
                "reputation": 0.08,
                "health": 0.15,
                "growth": 0.09,
            },
            "dev": {
                "cash": -1.00,
                "clients": 2.0,
                "reputation": 0.08,
                "health": 0.10,
                "growth": 0.12,
            },
        },

        "event": {
            "title": "⭐ Un influenceur parle de votre marque",
            "description": (
                "Un influenceur connu découvre votre produit "
                "et le recommande à son audience."
            ),
            "effects": {
                "clients": 220,
                "reputation": 10,
                "health": 0,
                "growth": 10,
            }
        }
    },

    {
        "title": "🤖 Startup IA face à un concurrent",
        "description": (
            "Votre startup développe une solution d'intelligence artificielle. "
            "Un concurrent mieux financé arrive sur le marché."
        ),

        "initial": {
            "cash": 100000,
            "clients": 400,
            "reputation": 58,
            "health": 76,
            "growth": 4,
        },

        "effects": {
            "marketing": {
                "cash": -1.00,
                "clients": 3.5,
                "reputation": 0.12,
                "health": -0.04,
                "growth": 0.10,
            },
            "rnd": {
                "cash": -1.00,
                "clients": 1.0,
                "reputation": 0.10,
                "health": 0.03,
                "growth": 0.20,
            },
            "recrutement": {
                "cash": -1.00,
                "clients": 1.8,
                "reputation": 0.08,
                "health": 0.16,
                "growth": 0.14,
            },
            "dev": {
                "cash": -1.00,
                "clients": 2.8,
                "reputation": 0.10,
                "health": 0.12,
                "growth": 0.18,
            },
        },

        "event": {
            "title": "⚔️ Un concurrent baisse ses prix",
            "description": (
                "Votre principal concurrent baisse ses prix de 30%. "
                "Vous risquez de perdre des clients."
            ),
            "effects": {
                "clients": -90,
                "reputation": -4,
                "health": -5,
                "growth": -5,
            }
        }
    },
]