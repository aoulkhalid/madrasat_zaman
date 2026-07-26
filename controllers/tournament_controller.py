"""
controllers/tournament_controller.py
Contrôleur principal — orchestre le tournoi et coordonne les pages
"""
import random
from PyQt5.QtCore import QObject, pyqtSignal
from models.tournament import Tournament
from models.match      import Match
from models.team       import Team


class TournamentController(QObject):
    """Pont entre le modèle tournoi et les pages PyQt5."""

    # Signaux
    match_started   = pyqtSignal(object)   # Match
    match_ended     = pyqtSignal(object)   # Match
    tournament_over = pyqtSignal(object)   # Team (champion)
    turn_changed    = pyqtSignal(object)   # Team (équipe active)
    score_updated   = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.tournament = Tournament()
        self._game_data_indices = {
            "quiz": 0, "logo": 0, "diff": 0
        }

    # ── Accès ─────────────────────────────────────────────────────────────────

    @property
    def current_match(self) -> Match:
        return self.tournament.current_match()

    @property
    def current_team(self) -> Team:
        return self.current_match.current_team

    @property
    def score1(self) -> int:
        return self.current_match.team1.score

    @property
    def score2(self) -> int:
        return self.current_match.team2.score

    def is_final(self) -> bool:
        return self.tournament.is_final()

    # ── Actions jeu ───────────────────────────────────────────────────────────

    def answer(self, game: str, correct: bool) -> int:
        """
        Enregistre une réponse. Retourne les points accordés.
        """
        from config import POINTS_CORRECT, POINTS_WRONG
        pts = POINTS_CORRECT if correct else POINTS_WRONG
        self.current_match.record_answer(game, pts)
        self.score_updated.emit()
        return pts

    def next_turn(self):
        """Passe au tour suivant (après réponse + délai visuel)."""
        self.current_match.next_turn()
        self.turn_changed.emit(self.current_team)

    # ── Fin de match ──────────────────────────────────────────────────────────

    def end_match(self) -> bool:
        """
        Termine le match actuel.
        Retourne True si le tournoi est terminé (après la finale).
        """
        done = self.tournament.advance()
        if done:
            self.tournament_over.emit(self.tournament.champion)
        else:
            self.match_ended.emit(self.tournament.matches[
                self.tournament.current_match_idx - 1])
        return done

    # ── Données de jeu (index slice par match) ────────────────────────────────

    def get_quiz_slice(self):
        """Retourne les 20 questions du match actuel."""
        from games.quiz_data import ALL_QUESTIONS
        idx   = self.tournament.current_match_idx
        start = idx * 50
        return ALL_QUESTIONS[start:start + 50]

    def get_logo_slice(self):
        """Retourne les 40 logos du match actuel."""
        from games.logo_data import ALL_LOGOS
        idx   = self.tournament.current_match_idx
        start = idx * 40
        return ALL_LOGOS[start:start + 40]

    def get_diff_slice(self):
        """Retourne les 10 paires du match actuel."""
        from games.diff_data import ALL_DIFFS
        idx   = self.tournament.current_match_idx
        start = idx * 10
        data  = ALL_DIFFS[start:start + 10]
        # Cycler si pas assez de données
        if len(data) < 10:
            import itertools
            data = list(itertools.islice(itertools.cycle(ALL_DIFFS), 10))
        return data

    # ── Reset ─────────────────────────────────────────────────────────────────

    def reset(self):
        self.tournament.reset()
        self.score_updated.emit()

    def award_points_to(self, team, game: str, pts: int):
        """Crédite des points à une équipe précise (jeux à score variable comme Le Code Secret)."""
        self.current_match.record_answer_for(team, game, pts)
        self.score_updated.emit()
        return pts

    # ── Sélection de données variée par match (anti-répétition) ───────────────

    def _pick_slice(self, pool, count, match_idx, salt=0):
        """Sélectionne `count` éléments de `pool` en variant nettement selon
        le match — via un tirage pseudo-aléatoire propre à chaque couple
        (match_idx, salt) — plutôt qu'un cycle modulo qui peut retomber sur
        les mêmes éléments quand la banque de données est petite ou que sa
        taille est un multiple de ce qui est consommé par match.

        `salt` permet de différencier plusieurs tirages au sein d'un même
        match (ex. tentative équipe A vs tentative équipe B pour un même
        match_idx), pour qu'elles ne reçoivent pas non plus les mêmes données.
        """
        rng = random.Random((match_idx * 1000) + salt)
        if len(pool) >= count:
            return rng.sample(pool, count)
        # Pas assez d'éléments uniques : on complète en répétant après mélange
        shuffled = pool[:]
        rng.shuffle(shuffled)
        result = []
        while len(result) < count:
            result.extend(shuffled)
        return result[:count]

    def get_element_slice(self):
        """Retourne les combinaisons du match actuel (variées entre matchs)."""
        from games.element_data import ALL_COMBOS
        from config import ELEMENT_PER_MATCH
        idx = self.tournament.current_match_idx
        return self._pick_slice(ALL_COMBOS, ELEMENT_PER_MATCH, idx)

    def get_heist_slice(self, attempt_offset: int):
        """Retourne les missions pour une tentative de braquage (variées entre matchs et tentatives)."""
        from games.heist_data import ALL_MISSIONS
        from config import HEIST_MISSIONS_PER_ATTEMPT
        idx = self.tournament.current_match_idx
        return self._pick_slice(ALL_MISSIONS, HEIST_MISSIONS_PER_ATTEMPT, idx, salt=attempt_offset)

    def get_cyber_slice(self, attempt_offset: int):
        """Retourne les indices pour une tentative d'enquête (variés entre matchs et tentatives)."""
        from games.cyber_data import ALL_CLUES
        from config import CYBER_CLUES_PER_ATTEMPT
        idx = self.tournament.current_match_idx
        return self._pick_slice(ALL_CLUES, CYBER_CLUES_PER_ATTEMPT, idx, salt=attempt_offset)

    def get_blindtest_slice(self):
        """Retourne les extraits du match actuel (variés entre matchs)."""
        from games.blindtest_data import ALL_TRACKS
        from config import BLINDTEST_TRACKS_PER_MATCH
        idx = self.tournament.current_match_idx
        return self._pick_slice(ALL_TRACKS, BLINDTEST_TRACKS_PER_MATCH, idx)

    def get_investment_slice(self):
        """Retourne les scénarios du match actuel (variés entre matchs)."""
        from games.investment_data import ALL_SCENARIOS
        from config import INVESTMENT_ROUNDS_PER_MATCH
        idx = self.tournament.current_match_idx
        return self._pick_slice(ALL_SCENARIOS, INVESTMENT_ROUNDS_PER_MATCH, idx)

    def get_transmission_slice(self):
        """Retourne les rounds du match actuel (variés entre matchs)."""
        from games.transmission_data import ALL_ROUNDS
        from config import TRANSMISSION_PER_MATCH
        idx = self.tournament.current_match_idx
        return self._pick_slice(ALL_ROUNDS, TRANSMISSION_PER_MATCH, idx)

    def get_memory_pool(self, round_idx: int, pairs: int):
        """Retourne les `pairs` noms de fichiers d'images pour une manche du
        Memory Challenge, variés entre les 3 matchs (chaque banque contient
        3x le nombre nécessaire — un lot différent par match_idx)."""
        from games.memory_data import EASY_IMAGES, MEDIUM_IMAGES, HARD_IMAGES
        pools = [EASY_IMAGES, MEDIUM_IMAGES, HARD_IMAGES]
        pool = pools[round_idx]
        match_idx = self.tournament.current_match_idx
        # Chaque banque est découpée en 3 tiers consécutifs (1 par match)
        third = len(pool) // 3
        start = (match_idx * third) % len(pool)
        segment = pool[start:start + third]
        if len(segment) < pairs:
            # Sécurité si la banque n'est pas un multiple exact de 3
            segment = (segment * ((pairs // max(len(segment), 1)) + 1))
        return segment[:pairs]