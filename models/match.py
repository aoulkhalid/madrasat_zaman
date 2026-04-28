"""models/match.py — Un match entre deux équipes"""
from models.team import Team

class Match:
    def __init__(self, match_id: int, label: str, team1: Team, team2: Team):
        self.match_id    = match_id
        self.label       = label
        self.team1       = team1
        self.team2       = team2
        self._turn_index = 0      # index global des tours (0=T1, 1=T2, 2=T1 ...)
        self.finished    = False
        self.winner      = None   # Team ou None
        # Stats par jeu
        self.game_history = []    # liste de dict {game, team, pts}

    @property
    def current_team(self) -> Team:
        """Équipe dont c'est le tour."""
        return self.team1 if self._turn_index % 2 == 0 else self.team2

    @property
    def other_team(self) -> Team:
        return self.team2 if self._turn_index % 2 == 0 else self.team1

    def next_turn(self):
        """Passe au tour suivant."""
        self._turn_index += 1

    def record_answer(self, game: str, pts: int):
        """Enregistre une réponse et crédite le score."""
        team = self.current_team
        team.add_score(pts)
        self.game_history.append({
            "game": game, "team": team.key, "pts": pts,
            "score1": self.team1.score, "score2": self.team2.score,
        })

    def determine_winner(self) -> Team:
        """Calcule et fixe le vainqueur."""
        if self.team1.score > self.team2.score:
            self.winner = self.team1
        elif self.team2.score > self.team1.score:
            self.winner = self.team2
        else:
            # Égalité → équipe 1 par défaut (ou random)
            self.winner = self.team1
        self.finished = True
        return self.winner

    def __repr__(self):
        return (f"Match({self.label}: {self.team1.key}={self.team1.score} "
                f"vs {self.team2.key}={self.team2.score})")
