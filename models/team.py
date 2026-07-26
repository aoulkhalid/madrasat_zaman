"""models/team.py — Entité Équipe"""

class Team:
    def __init__(self, key: str, name: str, color: str, light: str, emoji: str):
        self.key    = key
        self.name   = name
        self.color  = color
        self.light  = light
        self.emoji  = emoji
        self.score  = 0

    def add_score(self, pts: int):
        self.score += pts

    def reset(self):
        self.score = 0

    def __repr__(self):
        return f"Team({self.key}: {self.score}pts)"
