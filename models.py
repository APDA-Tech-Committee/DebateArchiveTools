class Debater:
    def __init__(self, id, name, isVarsity):
        self.id = id
        self.name = name
        self.isVarsity = isVarsity

class Team:
    def __init__(self, id, name, debater1, debater2, rounds=None):
        self.id = id
        self.name = name
        self.debater1 = debater1
        self.debater2 = debater2
        self.rounds = rounds if rounds is not None else []

class Judge:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Round:
    def __init__(self, id, name, team1, team2, chair, roundNumber=0, judges=None, speaks=None, ranks=None):
        self.id = id
        self.roundNumber = roundNumber
        self.name = name
        self.team1 = team1
        self.team2 = team2
        self.chair = chair
        self.judges = judges if judges is not None else []
        self.ranks = ranks if ranks is not None else {"team1":{"debater1":"","debater2":""}, "team2":{"debater1":"","debater2":""}}
        self.speaks = speaks if speaks is not None else {"team1":{"debater1":"","debater2":""}, "team2":{"debater1":"","debater2":""}}
