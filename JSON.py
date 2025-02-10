import json
from models import *

def deserialize_json(filepath):
    teams = {}
    debaters = {}
    judges = {}
    rounds = {}

    with open(filepath, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    tab_cards = json_data.get("tab_cards", {})

    for team_name, team_data in tab_cards.items():
        deb1_name = team_data.get("debater_1", "")
        deb1_status = team_data.get("debater_1_status", "Novice") == "Varsity"
        deb1 = Debater(id=team_name + "_1", name=deb1_name, isVarsity=deb1_status)
        debaters[deb1.id] = deb1

        deb2 = None
        if "debater_2" in team_data:
            deb2_name = team_data.get("debater_2", "")
            deb2_status = team_data.get("debater_2_status", "Novice") == "Varsity"
            deb2 = Debater(id=team_name + "_2", name=deb2_name, isVarsity=deb2_status)
            debaters[deb2.id] = deb2

        team = Team(id=team_name, name=team_name, debater1=deb1, debater2=deb2, rounds=[])
        teams[team_name] = team

    for team_name, team_data in tab_cards.items():
        team = teams[team_name]

        for round_data in team_data.get("rounds", []):
            id = round_data.get("id", -1)
            if id in rounds:
                round_obj = rounds[id]
                continue
            chair_name = round_data.get("chair", "Unknown Judge")
            if chair_name not in judges:
                judges[chair_name] = Judge(id=chair_name, name=chair_name)
            chair = judges[chair_name]

            opponent_name = round_data.get("opponent", {}).get("name", "Unknown Team")
            opponent_team = teams.get(opponent_name, None)

            gov = False
            if round_data.get("side", "") == "G":
                gov = True
            
            winner = False
            if round_data.get("result", "") == "W":
                winner = True
            round_obj = Round(
                id=round_data.get("round_id", -1),
                name=f"Round {round_data.get('round_number', -1)}",
                team1=team,
                team2=opponent_team,
                chair=chair,
                gov=gov,
                winner=winner,
                roundNumber=round_data.get("round_number", -1),
                judges=[],
                speaks={"team1": {"debater1": -1, "debater2": -1}},
                ranks={"team1": {"debater1": -1, "debater2": -1}}
            )

            for wing_name in round_data.get("wings", []):
                if wing_name not in judges:
                    judges[wing_name] = Judge(id=wing_name, name=wing_name)
                round_obj.judges.append(judges[wing_name])

            debater1_stats = round_data.get("debater1", [(-1, -1)])
            debater2_stats = round_data.get("debater2", [(-1, -1)])

            round_obj.speaks["team1"]["debater1"], round_obj.ranks["team1"]["debater1"] = debater1_stats[0]
            round_obj.speaks["team1"]["debater2"], round_obj.ranks["team1"]["debater2"] = debater2_stats[0] if debater2_stats else (-1, -1)

            team.rounds.append(round_obj)
            rounds[round_obj.id] = round_obj

    return {
        "teams": list(teams.values()),
        "debaters": list(debaters.values()),
        "judges": list(judges.values()),
        "rounds": list(rounds.values())
    }
