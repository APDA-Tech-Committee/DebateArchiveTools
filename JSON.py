import json
from models import *

def deserialize_json(filepath):
    teams = {}
    debaters = {}
    judges = {}
    rounds = []

    with open(filepath, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    tab_cards = json_data.get("tab_cards", {})

    for team_name, team_data in tab_cards.items():
        print("here1")
        deb1_name = team_data.get("debater_1", "")
        deb1_status = team_data.get("debater_1_status", "Novice") == "Varsity"
        deb1 = Debater(id=team_name + "_1", name=deb1_name, isVarsity=deb1_status)
        debaters[deb1.id] = deb1

        deb2 = None
        if "debater_2" in team_data:
            print("here2")
            deb2_name = team_data.get("debater_2", "")
            deb2_status = team_data.get("debater_2_status", "Novice") == "Varsity"
            deb2 = Debater(id=team_name + "_2", name=deb2_name, isVarsity=deb2_status)
            debaters[deb2.id] = deb2

        team = Team(id=team_name, name=team_name, debater1=deb1, debater2=deb2, rounds=[])
        teams[team_name] = team

    for team_name, team_data in tab_cards.items():
        print("here3")
        team = teams[team_name]

        for round_data in team_data.get("rounds", []):
            print("here4")
            chair_name = round_data.get("chair", "Unknown Judge")
            if chair_name not in judges:
                print("here5")
                judges[chair_name] = Judge(id=chair_name, name=chair_name)
            chair = judges[chair_name]

            opponent_name = round_data.get("opponent", {}).get("name", "Unknown Team")
            opponent_team = teams.get(opponent_name, None)

            round_obj = Round(
                id=round_data.get("round_id", -1),
                name=f"Round {round_data.get('round_number', -1)}",
                team1=team,
                team2=opponent_team,
                chair=chair,
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
            rounds.append(round_obj)

    return {
        "tournament_name": "Sample Tournament",
        "teams": list(teams.values()),
        "debaters": list(debaters.values()),
        "judges": list(judges.values()),
        "rounds": rounds
    }

def serialize_to_json(teams):
    output_data = {}

    for team_name, team in teams.items():
        team_data = {
            "team_name": team.name,
            "debater_1": team.debater1.name if team.debater1 else "",
            "debater_1_status": "Varsity" if team.debater1 and team.debater1.isVarsity else "Novice",
            "rounds": []
        }
        if team.debater2:
            team_data["debater_2"] = team.debater2.name
            team_data["debater_2_status"] = "Varsity" if team.debater2.isVarsity else "Novice"

        for round_obj in team.rounds:
            round_data = {
                "round_id": round_obj.id if round_obj.id is not None else -1,
                "round_number": round_obj.roundNumber if round_obj.roundNumber is not None else -1,
                "chair": round_obj.chair.name if round_obj.chair else "Unknown Judge",
                "wings": [judge.name for judge in round_obj.judges] if round_obj.judges else [],
                "opponent": {
                    "name": round_obj.team2.name if round_obj.team2 else "Unknown Team",
                },
                "debater1": [(round_obj.speaks["team1"].get("debater1", -1), round_obj.ranks["team1"].get("debater1", -1))],
                "debater2": [(round_obj.speaks["team1"].get("debater2", -1), round_obj.ranks["team1"].get("debater2", -1))] if team.debater2 else []
            }
            team_data["rounds"].append(round_data)

        output_data[team_name] = team_data

    return json.dumps(output_data, indent=4)
