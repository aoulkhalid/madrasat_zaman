"""
controllers/tournament_controller.py
Contrôleur principal — orchestre le tournoi et coordonne les pages
"""
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
        start = idx * 20
        return ALL_QUESTIONS[start:start + 20]

    def get_logo_slice(self):
        """Retourne les 20 logos du match actuel."""
        from games.logo_data import ALL_LOGOS
        idx   = self.tournament.current_match_idx
        start = idx * 20
        return ALL_LOGOS[start:start + 20]

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
