# -*- coding: utf-8 -*-
"""
games/memory_data.py — 🧠 Memory Challenge

Les valeurs ci-dessous sont des NOMS DE FICHIERS à placer dans :
    assets/images/memory/

Formats acceptés : .png, .jpg, .jpeg, .webp
Si un fichier est introuvable, la carte affiche automatiquement un repli
emoji (❓ générique) à la place — l'app ne plantera jamais, mais mets bien
tes images pour un rendu correct.

Chaque banque contient 3x le nombre d'images nécessaires par manche, pour
que chaque match (Demi 1 / Demi 2 / Finale) pioche un lot DIFFÉRENT via
tournament_controller.get_memory_pool() — plutôt que de toujours montrer
exactement les mêmes images à chaque match.

Tailles nécessaires PAR MANCHE (pas au total) :
  - 5  pour la Manche 1 (facile)
  - 8  pour la Manche 2 (moyen)
  - 10 pour la Manche 3 (difficile)
"""

EASY_IMAGES = [
    # Match 1 (Demi-finale 1)
    "computer.png", "cat.png", "car.png", "tree.png", "ball.png",
    # Match 2 (Demi-finale 2)
    "book.png", "sun.png", "moon.png", "star.png", "house.png",
    # Match 3 (Finale)
    "flower.png", "fish.png", "bird.png", "clock.png", "key.png",
]

MEDIUM_IMAGES = [
    # Match 1 (Demi-finale 1)
    "desktop.png", "robot.png", "dog.png", "earth.png",
    "smartphone.png", "rocket.png", "guitar.png", "camera.png",
    # Match 2 (Demi-finale 2)
    "airplane.png", "bicycle.png", "umbrella.png", "compass.png",
    "telescope.png", "lightbulb.png", "anchor.png", "hourglass.png",
    # Match 3 (Finale)
    "castle.png", "volcano.png", "windmill.png", "lighthouse.png",
    "satellite.png", "submarine.png", "balloon.png", "kite.png",
]

HARD_IMAGES = [
    # Match 1 (Demi-finale 1)
    "unicorn.png", "dragon.png", "mask.png", "crystal_ball.png", "moai.png",
    "ufo.png", "circus_tent.png", "rainbow.png", "puzzle.png", "target.png",
    # Match 2 (Demi-finale 2)
    "phoenix.png", "griffin.png", "compass_rose.png", "hourglass_gold.png",
    "labyrinth.png", "comet.png", "carnival_mask.png", "prism.png",
    "chess_king.png", "treasure_chest.png",
    # Match 3 (Finale)
    "kraken.png", "pegasus.png", "sphinx.png", "meteor.png",
    "clockwork.png", "aurora.png", "obelisk.png", "kaleidoscope.png",
    "chess_queen.png", "golden_key.png",
]
