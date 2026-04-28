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
            # Demi-finale 1 terminée → préparer semi-finale 2
            self.current_match_idx = 1
            return False
        elif self.current_match_idx == 1:
            # Demi-finale 2 terminée → créer la finale
            w1 = self.matches[0].winner
            w2 = self.matches[1].winner
            # Reset scores pour la finale
            w1.reset()
            w2.reset()
            s = TOURNAMENT_STRUCTURE[2]
            final = Match(s["id"], s["label"], w1, w2)
            self.matches[2] = final
            self.current_match_idx = 2
            return False
        else:
            # Finale terminée
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
