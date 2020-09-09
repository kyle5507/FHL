class Player:
    def __init__(self, nick, skilllvl, won, loss, streak, pos, points):
        self.nick = nick
        self.skill = skilllvl
        self.won = won
        self.loss = loss
        self.streak = streak
        self.pos = pos
        self.points = points

    def __repr__(self):
        if self.streak < 1:
            return f"{self.pos}. {self.nick} (lvl:{self.skill})" \
                   f"\nW: {self.won} L: {self.loss}" \
                   f" ({round((self.won / (self.won + self.loss)),2) if self.loss != 0 else 1.0})" \
                   f"\nPoints: {self.points}"
        else:
            return f"{self.pos}. {self.nick} (lvl:{self.skill})" \
                   f"\nW: {self.won} L: {self.loss}" \
                   f" ({round((self.won / (self.won + self.loss)),2) if self.loss != 0 else 1.0}) :fire: {self.streak}" \
                   f"\nPoints: {self.points}"
