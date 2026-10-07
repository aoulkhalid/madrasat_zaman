# -*- coding: utf-8 -*-
"""
games/element_data.py — Science Fusion

Questions scientifiques pour étudiants niveau 2ème année faculté / Bac+3.

Format :
    {
        "a": ...,
        "b": ...,
        "answer": <index 0-3>,
        "choices": [4 réponses]
    }

Champs optionnels :
    "category"
    "domain"
    "difficulty"
    "level"
    "explanation"
    "points"
    "time_limit"

Variable principale :
    ALL_COMBOS
"""

# ──────────────────────────────────────────────────────────────
# Métadonnées de gameplay
# ──────────────────────────────────────────────────────────────

LEVEL_NAMES = {
    1: "Connaissance",
    2: "Compréhension",
    3: "Application",
    4: "Raisonnement",
    5: "Expert",
}

POINTS_BY_DIFFICULTY = {
    1: 100,
    2: 150,
    3: 200,
    4: 300,
    5: 500,
}

TIME_BY_DIFFICULTY = {
    1: 20,
    2: 25,
    3: 30,
    4: 40,
    5: 50,
}

CATEGORY_ICONS = {
    "Chimie": "⚗️",
    "Physique": "⚛️",
    "Biologie": "🧬",
    "Géologie": "🌍",
    "Astronomie": "🌌",
    "Informatique": "💻",
    "Intelligence artificielle": "🤖",
    "Mathématiques": "📐",
    "Électricité": "⚡",
}


def _q(a, b, answer, choices, category, difficulty, explanation, domain=None):
    """Construit une entrée au format historique + champs optionnels."""

    item = {
        "a": a,
        "b": b,
        "answer": answer,
        "choices": choices,
        "category": category,
        "difficulty": difficulty,
        "explanation": explanation,
    }

    if domain:
        item["domain"] = domain

    return item


# ──────────────────────────────────────────────────────────────
# QUESTIONS
# ──────────────────────────────────────────────────────────────

ALL_COMBOS = [

    # ============================================================
    # 🧪 CHIMIE — Niveau Bac+3
    # ============================================================

    _q(
        "🧪 Acide faible HA",
        "⚗️ Solution tampon",
        1,
        [
            "pH = pKa - log([A⁻]/[HA])",
            "pH = pKa + log([A⁻]/[HA])",
            "pH = Ka + log([A⁻]/[HA])",
            "pH = -log(Ka[A⁻]/[HA])"
        ],
        "Chimie",
        5,
        "L'équation de Henderson-Hasselbalch donne pH = pKa + log([A⁻]/[HA]).",
        "Chimie analytique"
    ),

    _q(
        "⚗️ Réaction d'oxydo-réduction",
        "🔋 Équation de Nernst",
        2,
        [
            "E = E° + (RT/nF)ln(Q)",
            "E = E° - (RT/F)ln(Q)",
            "E = E° - (RT/nF)ln(Q)",
            "E = E° + (nF/RT)ln(Q)"
        ],
        "Chimie",
        5,
        "Pour une réaction de réduction, E = E° - (RT/nF)ln(Q).",
        "Électrochimie"
    ),

    _q(
        "⚛️ Cinétique chimique",
        "📈 Équation d'Arrhenius",
        0,
        [
            "k = A exp(-Ea/RT)",
            "k = A exp(Ea/RT)",
            "k = Ea exp(-A/RT)",
            "k = RT exp(-Ea/A)"
        ],
        "Chimie",
        4,
        "La loi d'Arrhenius relie la constante cinétique à l'énergie d'activation.",
        "Cinétique"
    ),

    _q(
        "⚗️ Thermodynamique",
        "🔥 Spontanéité",
        3,
        [
            "ΔG = ΔH + TΔS",
            "ΔG = ΔH - ΔS/T",
            "ΔG = ΔS - TΔH",
            "ΔG = ΔH - TΔS"
        ],
        "Chimie",
        4,
        "À température et pression constantes, ΔG = ΔH - TΔS.",
        "Thermodynamique"
    ),

    _q(
        "🧪 Substitution nucléophile",
        "🔬 Mécanisme SN2",
        1,
        [
            "Deux étapes avec carbocation intermédiaire",
            "Une seule étape avec attaque arrière",
            "Formation obligatoire d'un radical",
            "Réarrangement obligatoire du squelette"
        ],
        "Chimie",
        5,
        "La SN2 est concertée et implique une attaque nucléophile par l'arrière.",
        "Chimie organique"
    ),


    # ============================================================
    # 📐 MATHÉMATIQUES — Niveau Bac+3
    # ============================================================

    _q(
        "📐 Matrice carrée A",
        "🔢 Valeurs propres",
        2,
        [
            "det(A + λI) = 0",
            "det(A - λI) = 1",
            "det(A - λI) = 0",
            "det(λA - I) = 0"
        ],
        "Mathématiques",
        4,
        "Les valeurs propres sont les racines du polynôme caractéristique det(A - λI).",
        "Algèbre linéaire"
    ),

    _q(
        "📊 Série numérique",
        "∞ Somme géométrique",
        0,
        [
            "Σqⁿ converge si |q| < 1",
            "Σqⁿ converge si |q| > 1",
            "Σqⁿ converge seulement si q = 1",
            "Σqⁿ converge pour tout q réel"
        ],
        "Mathématiques",
        4,
        "La série géométrique converge exactement lorsque |q| < 1.",
        "Analyse"
    ),

    _q(
        "📈 Développement de Taylor",
        "🧮 Fonction f(x)",
        3,
        [
            "f(x) = f(0) + xf'(0)",
            "f(x) = Σ f⁽ⁿ⁾(0)/n!",
            "f(x) = Σ f⁽ⁿ⁾(x)/n!",
            "f(x) = Σ f⁽ⁿ⁾(0)xⁿ/n!"
        ],
        "Mathématiques",
        5,
        "Le développement de Taylor autour de 0 utilise f⁽ⁿ⁾(0)xⁿ/n!.",
        "Analyse"
    ),

    _q(
        "🎲 Probabilité conditionnelle",
        "📊 Bayes",
        1,
        [
            "P(A|B)=P(A)P(B)",
            "P(A|B)=P(B|A)P(A)/P(B)",
            "P(A|B)=P(A∩B)/P(A)",
            "P(A|B)=P(B)/P(A)"
        ],
        "Mathématiques",
        4,
        "Le théorème de Bayes donne P(A|B)=P(B|A)P(A)/P(B).",
        "Probabilités"
    ),

    _q(
        "📐 Équation différentielle",
        "📈 y' = ay",
        2,
        [
            "y(x)=a eˣ",
            "y(x)=e^(ax)",
            "y(x)=Ce^(ax)",
            "y(x)=Cx^a"
        ],
        "Mathématiques",
        4,
        "La solution générale de y'=ay est y=Ce^(ax).",
        "Équations différentielles"
    ),


    # ============================================================
    # 💻 INFORMATIQUE — Niveau Bac+3
    # ============================================================

    _q(
        "💻 Algorithme de Dijkstra",
        "🛣️ Plus court chemin",
        1,
        [
            "Fonctionne uniquement avec des poids négatifs",
            "Nécessite un graphe acyclique",
            "Suppose des poids non négatifs",
            "Fonctionne uniquement sur les graphes orientés"
        ],
        "Informatique",
        4,
        "Dijkstra est correct lorsque tous les poids des arêtes sont non négatifs.",
        "Algorithmique"
    ),

    _q(
        "⏱️ Complexité algorithmique",
        "🔁 Deux boucles imbriquées",
        0,
        [
            "O(log n)",
            "O(n)",
            "O(n²)",
            "O(2ⁿ)"
        ],
        "Informatique",
        4,
        "Deux boucles parcourant chacune n éléments donnent généralement O(n²).",
        "Complexité"
    ),

    _q(
        "🗃️ Base de données relationnelle",
        "🔐 Troisième forme normale",
        2,
        [
            "Supprimer toutes les clés étrangères",
            "Autoriser les dépendances transitives",
            "Éliminer les dépendances fonctionnelles transitives",
            "Remplacer toutes les tables par une seule"
        ],
        "Informatique",
        5,
        "La 3NF élimine notamment les dépendances fonctionnelles transitives entre attributs non-clés.",
        "Bases de données"
    ),

    _q(
        "🧠 Mémoire virtuelle",
        "💾 Pagination",
        3,
        [
            "Réduire la fréquence du processeur",
            "Mapper des pages virtuelles vers des cadres physiques",
            "Compresser automatiquement tous les programmes",
            "Supprimer définitivement la mémoire RAM"
        ],
        "Informatique",
        4,
        "La pagination permet de mapper les pages virtuelles vers des cadres en mémoire physique.",
        "Systèmes"
    ),

    _q(
        "🌐 TCP",
        "📡 Contrôle de congestion",
        1,
        [
            "ARP",
            "Slow Start",
            "DNS",
            "NAT"
        ],
        "Informatique",
        4,
        "TCP utilise notamment Slow Start pour contrôler progressivement le débit d'émission.",
        "Réseaux"
    ),


    # ============================================================
    # 🤖 INTELLIGENCE ARTIFICIELLE — Niveau Bac+3
    # ============================================================

    _q(
        "🤖 Régression logistique",
        "📉 Fonction de coût",
        2,
        [
            "Erreur quadratique uniquement",
            "Hinge loss uniquement",
            "Binary cross-entropy",
            "Distance euclidienne"
        ],
        "Intelligence artificielle",
        4,
        "La régression logistique est généralement entraînée avec la binary cross-entropy.",
        "Machine Learning"
    ),

    _q(
        "🧠 Réseau de neurones",
        "🔄 Backpropagation",
        0,
        [
            "Calculer le gradient de la fonction de coût",
            "Supprimer les poids aléatoires",
            "Augmenter automatiquement le nombre de classes",
            "Transformer toutes les données en images"
        ],
        "Intelligence artificielle",
        5,
        "La rétropropagation calcule efficacement les gradients nécessaires à la mise à jour des poids.",
        "Deep Learning"
    ),

    _q(
        "📊 PCA",
        "🔢 Réduction dimensionnelle",
        3,
        [
            "Maximiser la variance projetée",
            "Minimiser systématiquement toutes les distances",
            "Maximiser le nombre de variables",
            "Supprimer uniquement les valeurs manquantes"
        ],
        "Intelligence artificielle",
        5,
        "La première composante principale maximise la variance des données projetées.",
        "Machine Learning"
    ),

    _q(
        "⚖️ Régularisation L2",
        "🎯 Fonction de coût",
        1,
        [
            "Ajouter λΣ|w|",
            "Ajouter λΣw²",
            "Multiplier la loss par λ²",
            "Supprimer les biais"
        ],
        "Intelligence artificielle",
        4,
        "La régularisation L2 ajoute généralement λΣw² à la fonction de coût.",
        "Optimisation"
    ),

    _q(
        "🧠 Overfitting",
        "📚 Généralisation",
        2,
        [
            "Erreur train élevée et test faible",
            "Erreur train et test toujours nulles",
            "Erreur train faible mais erreur test élevée",
            "Absence totale de paramètres"
        ],
        "Intelligence artificielle",
        4,
        "L'overfitting correspond typiquement à une excellente performance d'entraînement mais une mauvaise généralisation.",
        "Machine Learning"
    ),


    # ============================================================
    # ⚛️ PHYSIQUE — Niveau Bac+3
    # ============================================================

    _q(
        "⚛️ Oscillateur harmonique",
        "📈 Énergie mécanique",
        3,
        [
            "E = mv",
            "E = kx",
            "E = 1/2kx",
            "E = 1/2kx² + 1/2mv²"
        ],
        "Physique",
        4,
        "L'énergie totale de l'oscillateur est la somme des énergies potentielle et cinétique.",
        "Mécanique"
    ),

    _q(
        "🌌 Électromagnétisme",
        "⚡ Loi de Gauss",
        0,
        [
            "∮E·dS = Q/ε₀",
            "∮E·dS = ε₀Q",
            "∮E·dS = Qε₀",
            "∮E·dS = 0 pour toute charge"
        ],
        "Physique",
        5,
        "Le flux électrique à travers une surface fermée vaut Qint/ε₀.",
        "Électromagnétisme"
    ),

    _q(
        "🔥 Thermodynamique",
        "♨️ Premier principe",
        1,
        [
            "ΔU = Q - W si W est reçu",
            "ΔU = Q + W si W est reçu",
            "ΔU = QW",
            "ΔU = Q/W"
        ],
        "Physique",
        4,
        "Avec W défini comme le travail reçu par le système, ΔU = Q + W.",
        "Thermodynamique"
    ),

    _q(
        "⚡ Circuit RC",
        "⏱️ Constante de temps",
        2,
        [
            "τ = R/C",
            "τ = C/R",
            "τ = RC",
            "τ = R + C"
        ],
        "Physique",
        4,
        "La constante de temps d'un circuit RC est τ = RC.",
        "Électricité"
    ),

    _q(
        "🌊 Onde progressive",
        "📐 Relation fondamentale",
        1,
        [
            "v = λf",
            "v = λ/f",
            "v = f/λ",
            "v = λ + f"
        ],
        "Physique",
        4,
        "La vitesse de propagation est liée à la longueur d'onde et à la fréquence par v = λf.",
        "Ondes"
    ),


    # ============================================================
    # 🧬 BIOLOGIE — Niveau Bac+3
    # ============================================================

    _q(
        "🧬 Génétique des populations",
        "📊 Hardy-Weinberg",
        0,
        [
            "p + q = 2",
            "p² + 2pq + q² = 1",
            "p² + q² = 2",
            "pq = 1"
        ],
        "Biologie",
        4,
        "Sous les hypothèses de Hardy-Weinberg, p² + 2pq + q² = 1.",
        "Génétique"
    ),

    _q(
        "🧬 Expression génétique",
        "🔬 Traduction",
        3,
        [
            "ADN → protéine directement",
            "ARN → ADN uniquement",
            "Protéine → ARN",
            "ARNm → chaîne polypeptidique"
        ],
        "Biologie",
        4,
        "Lors de la traduction, le ribosome utilise l'ARNm pour synthétiser une chaîne polypeptidique.",
        "Biologie moléculaire"
    ),

    _q(
        "🧪 Enzymologie",
        "📈 Michaelis-Menten",
        1,
        [
            "v = Vmax + [S]",
            "v = Vmax[S]/(Km + [S])",
            "v = Km/(Vmax[S])",
            "v = [S]/Km"
        ],
        "Biologie",
        5,
        "L'équation de Michaelis-Menten est v = Vmax[S]/(Km+[S]).",
        "Biochimie"
    ),

    _q(
        "🔬 Inhibition compétitive",
        "🧪 Enzyme",
        2,
        [
            "Vmax diminue et Km diminue",
            "Vmax augmente et Km diminue",
            "Vmax reste inchangée et Km apparent augmente",
            "Vmax et Km restent toujours inchangés"
        ],
        "Biologie",
        5,
        "Une inhibition compétitive augmente le Km apparent sans modifier Vmax.",
        "Enzymologie"
    ),

    _q(
        "🧬 Méiose",
        "🔀 Recombinaison génétique",
        3,
        [
            "Mutation uniquement",
            "Réplication de l'ADN",
            "Traduction des protéines",
            "Crossing-over"
        ],
        "Biologie",
        4,
        "Le crossing-over entre chromosomes homologues contribue à la diversité génétique.",
        "Génétique"
    ),


    # ============================================================
    # ⚡ ÉLECTRICITÉ / ÉLECTRONIQUE — Niveau Bac+3
    # ============================================================

    _q(
        "⚡ Lois de Kirchhoff",
        "🔌 Loi des nœuds",
        0,
        [
            "La somme des courants entrants égale la somme des courants sortants",
            "Tous les courants sont forcément nuls",
            "La tension est toujours nulle",
            "La résistance totale est toujours constante"
        ],
        "Électricité",
        4,
        "La loi des nœuds exprime la conservation de la charge électrique.",
        "Circuits électriques"
    ),

    _q(
        "🔌 Circuit RLC série",
        "📡 Résonance",
        2,
        [
            "XL = XC",
            "R = 0 obligatoirement",
            "XL = 2XC",
            "XL = R"
        ],
        "Électricité",
        5,
        "À la résonance d'un RLC série, les réactances inductive et capacitive se compensent.",
        "Électronique"
    ),

    _q(
        "⚡ Théorème de Thévenin",
        "🔋 Circuit équivalent",
        1,
        [
            "Une source de courant idéale uniquement",
            "Une source de tension en série avec une résistance",
            "Deux résistances en parallèle uniquement",
            "Un condensateur seul"
        ],
        "Électricité",
        4,
        "Tout réseau linéaire vu depuis deux bornes peut être remplacé par une source de Thévenin et une résistance série.",
        "Circuits électriques"
    ),

    _q(
        "📡 Courant alternatif",
        "⚙️ Impédance d'une bobine",
        3,
        [
            "ZL = R",
            "ZL = 1/(jωL)",
            "ZL = jωL",
            "ZL = ω/L"
        ],
        "Électricité",
        5,
        "L'impédance complexe d'une inductance idéale est ZL = jωL.",
        "Électrotechnique"
    ),

    _q(
        "🔋 Facteur de puissance",
        "📐 Circuit AC",
        1,
        [
            "cos φ = P/S",
            "cos φ = S/P",
            "cos φ = Q/P",
            "cos φ = P×S"
        ],
        "Électricité",
        4,
        "Le facteur de puissance est défini par cosφ = P/S.",
        "Électrotechnique"
    ),
]


# ──────────────────────────────────────────────────────────────
# Utilitaires
# ──────────────────────────────────────────────────────────────

def difficulty_bar(difficulty, total=10):
    """
    Barre de difficulté :
    difficulté 1 → ██░░░░░░░░
    difficulté 5 → ██████████
    """

    filled = max(
        0,
        min(total, difficulty * 2)
    )

    return "█" * filled + "░" * (total - filled)


def get_by_difficulty(level):
    """Retourne les questions d'un niveau de difficulté donné."""

    return [
        q
        for q in ALL_COMBOS
        if q["difficulty"] == level
    ]


def get_by_category(category):
    """Retourne les questions d'une catégorie donnée."""

    return [
        q
        for q in ALL_COMBOS
        if q["category"] == category
    ]


def validate_combos(combos=None):
    """
    Vérifie la cohérence structurelle des données.
    Retourne une liste d'erreurs.
    """

    combos = ALL_COMBOS if combos is None else combos

    errors = []
    seen = set()

    for i, q in enumerate(combos):

        tag = (
            f"#{i + 1} "
            f"({q.get('a')} + {q.get('b')})"
        )

        # Vérification du nombre de choix
        if len(q["choices"]) != 4:
            errors.append(
                f"{tag} : "
                f"{len(q['choices'])} choix au lieu de 4"
            )

        # Vérification des doublons
        if len(set(q["choices"])) != len(q["choices"]):
            errors.append(
                f"{tag} : choix en double"
            )

        # Vérification de la bonne réponse
        if (
            not isinstance(q["answer"], int)
            or not 0 <= q["answer"] < len(q["choices"])
        ):
            errors.append(
                f"{tag} : "
                f"index 'answer' invalide "
                f"({q['answer']})"
            )

        # Vérification difficulté
        if q.get("difficulty") not in LEVEL_NAMES:
            errors.append(
                f"{tag} : difficulté invalide"
            )

        # Vérification combinaison doublée
        if (q["a"], q["b"]) in seen:
            errors.append(
                f"{tag} : combinaison a+b en double"
            )

        seen.add(
            (q["a"], q["b"])
        )

    return errors


# ──────────────────────────────────────────────────────────────
# Test du fichier
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":

    problems = validate_combos()

    print(
        f"{len(ALL_COMBOS)} questions — "
        f"{len(problems)} problème(s)"
    )

    for p in problems:
        print(" -", p)