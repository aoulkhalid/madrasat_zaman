<<<<<<< HEAD
# madrasat_zaman
cs_club_evenement
=======
# 🎓 Madrasat Zaman v3 — Tournoi 4 Équipes

Application desktop interactive pour événement scolaire
**PyQt5 · Architecture MVC · Plein écran · Audio**

---

## 🏆 Tournoi
| Match | Équipes | Type |
|-------|---------|------|
| 1 | 🔵 A vs 🔴 B | Demi-finale 1 |
| 2 | 🟢 C vs 🟠 D | Demi-finale 2 |
| 3 | Vainqueur 1 vs Vainqueur 2 | **Finale** |

---

## 🚀 Lancement

```bash
cd mz_v3
python main.py
```

**Installation manuelle (si nécessaire) :**
```bash
pip install PyQt5 Pillow pygame
python main.py
```

**Prérequis :** Python 3.9+

---

## 📂 Structure
```
mz_v3/
├── main.py                    ← Point d'entrée
├── config.py                  ← Constantes + QSS global
├── models/
│   ├── team.py                ← Entité Équipe
│   ├── match.py               ← Entité Match (scores, alternance)
│   └── tournament.py          ← Gestion tournoi complet
├── controllers/
│   └── tournament_controller.py ← Orchestration + liaison UI
├── audio/
│   └── manager.py             ← Pygame audio (calme/stress/victoire)
├── widgets/
│   └── circular_timer.py      ← Timer circulaire QPainter
├── games/
│   ├── quiz_data.py           ← 60 questions (20/match)
│   ├── logo_data.py           ← 60 logos (20/match)
│   └── diff_data.py           ← 30 paires (10/match)
├── pages/
│   ├── base_page.py           ← Header, bandeau, scoreboard
│   ├── home_page.py           ← Accueil
│   ├── menu_page.py           ← Menu + état tournoi
│   ├── quiz_page.py           ← Quiz QCM chrono
│   ├── logo_page.py           ← Logo game (bonne/mauvaise)
│   ├── difference_page.py     ← Spot the difference
│   └── result_page.py         ← Résultats + bracket
└── utils/
    └── asset_generator.py     ← Génère 60 logos + 6 images + 3 sons
```

---

## 🎮 Logique jeu

- **Alternance :** tour 0 → E1, tour 1 → E2, tour 2 → E1 ...
- **Scoring :** +5 pts bonne réponse, 0 mauvaise
- **Chrono :** 35 secondes par question/logo/différence
- **Fin de match :** bouton "Terminer ce match" dans le menu

## ⌨️ Raccourcis
| Touche | Action |
|--------|--------|
| `Échap` | Plein écran ↔ Fenêtré |
| `F11` | Plein écran ↔ Fenêtré |

---

*Propulsé par CS Club*
# madrasat_zaman
>>>>>>> c355d80 (first commit)
