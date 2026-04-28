"""
games/diff_data.py — 30 paires d'images (10 par match)
Les images sont générées dans utils/asset_generator.py
Chaque entrée : { "left": str, "right": str, "diffs": [(cx,cy,r),...] }
"""

ALL_DIFFS = []

# Générer les 30 entrées dynamiquement (3 variantes × 10 répétitions par match)
_VARIANTS = [
    {   # Variante 1 — Paysage montagne
        "left": "diff_mtn_left.png", "right": "diff_mtn_right.png",
        "title": "Paysage de montagne",
        "diffs": [(280,38,20),(82,112,18),(172,208,18),(308,172,18),(58,198,16)],
    },
    {   # Variante 2 — Ville nocturne
        "left": "diff_city_left.png", "right": "diff_city_right.png",
        "title": "Paysage urbain",
        "diffs": [(260,50,20),(90,130,18),(190,190,18),(310,160,16),(70,210,18)],
    },
    {   # Variante 3 — Forêt tropicale
        "left": "diff_forest_left.png", "right": "diff_forest_right.png",
        "title": "Forêt tropicale",
        "diffs": [(270,40,20),(80,100,18),(180,200,18),(300,180,18),(60,220,16)],
    },
]

for match_i in range(3):
    for i in range(10):
        v = _VARIANTS[i % len(_VARIANTS)].copy()
        ALL_DIFFS.append(v)
