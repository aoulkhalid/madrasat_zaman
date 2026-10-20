"""models/tournament.py — Gestion complète du tournoi"""
from models.team  import Team
from models.match import Match
from config import TEAMS, TOURNAMENT_STRUCTURE

class Tournament:
    def __init__(self):
        # Instancier les 4 équipes
        self.teams: dict[str, Team] = {
            k: Team(k, v["name"], v["color"], v["light"], v["emoji"])
            for k, v in TEAMS.items()
        }
        self.matches: list[Match] = []
        self.current_match_idx    = 0
        self.champion: Team | None = None
        self._init_matches()

    def _init_matches(self):
        """Crée les 2 demi-finales (la finale sera créée après les semis)."""
        for s in TOURNAMENT_STRUCTURE[:2]:
            t1 = self.teams[s["team1"]]
            t2 = self.teams[s["team2"]]
            self.matches.append(Match(s["id"], s["label"], t1, t2))
        # Placeholder finale
        self.matches.append(None)

    def current_match(self) -> Match:
        return self.matches[self.current_match_idx]

    def advance(self) -> bool:
        """
        Détermine le vainqueur du match actuel et passe au suivant.
        Retourne True si le tournoi est terminé.
        """
        m = self.current_match()
        winner = m.determine_winner()

        if self.current_match_idx == 0:
            self.current_match_idx = 1
            return False

        elif self.current_match_idx == 1:
            w1 = self.matches[0].winner
            w2 = self.matches[1].winner

            # IMPORTANT : copies avec score 0 pour la finale.
            # On ne touche PAS aux Team des demi-finales, sinon leur score
            # est effacé avant l'affichage de la page résultat.
            f1 = Team(w1.key, w1.name, w1.color, w1.light, w1.emoji)
            f2 = Team(w2.key, w2.name, w2.color, w2.light, w2.emoji)

            s = TOURNAMENT_STRUCTURE[2]
            self.matches[2] = Match(s["id"], s["label"], f1, f2)
            self.current_match_idx = 2
            return False

        else:
            self.champion = winner
            return True

    def is_final(self) -> bool:
        return self.current_match_idx == 2

    def reset(self):
        for t in self.teams.values():
            t.reset()
        self.matches       = []
        self.current_match_idx = 0
        self.champion      = None
        self._init_matches()
