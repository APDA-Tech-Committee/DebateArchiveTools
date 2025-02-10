import csv
from models import *

GOV = "G"
OPP = "O"

def parse_csv(filepath):
    teams = {}
    debaters = {}
    judges = {}
    rounds = {}
    round_data = []
    
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        next(reader)  # Ignore header

        # First pass: Create teams and judges
        for row in reader:
            if row["Round"] == "Total" or row["Round"] is None:
                continue
            
            team_name = row["Team Name"]
            opponent_name = row["Opponent"]
            chair_name = row["Chair"]
            wings = row["Wing(s)"].split(" - ") if row["Wing(s)"] else []
            
            deb1_name = row["Debater 1"]
            deb1_status = row["N/V"] == "V"
            deb2_name = row["Debater 2"]
            deb2_status = row["N/V"] == "V"
            
            if deb1_name not in debaters:
                debaters[deb1_name] = Debater(deb1_name, deb1_name, deb1_status)
            if deb2_name not in debaters:
                debaters[deb2_name] = Debater(deb2_name, deb2_name, deb2_status)
            
            if team_name not in teams:
                teams[team_name] = Team(team_name, team_name, debaters[deb1_name], debaters[deb2_name])
            if opponent_name not in teams:
                teams[opponent_name] = Team(opponent_name, opponent_name, None, None)
            
            if chair_name not in judges:
                judges[chair_name] = Judge(chair_name, chair_name)
            for wing in wings:
                if wing not in judges:
                    judges[wing] = Judge(wing, wing)
            
            round_data.append(row)  # Store round data for second pass
    
    # Second pass: Create rounds
    for row in round_data:
        id = row["Round id"]
        if id in rounds:
            continue
        
        round_number = int(row["Round"])
        gov = (row["Gov/Opp"] == "G")
        winner = (row["Win/Loss"] == "W")
        team = teams[row["Team Name"]]
        opponent = teams[row["Opponent"]]
        chair = judges[row["Chair"]]
        round_judges = [judges[wing] for wing in row["Wing(s)"].split(" - ") if wing]
        
        
        deb1_speaks = float(row["Speaks"])
        deb1_ranks = float(row["Ranks"])
        deb2_speaks = float(row["Speaks"])
        deb2_ranks = float(row["Ranks"])
        
        round_obj = Round(
            name=f"Round {round_number}",
            id=id,
            team1=team,
            team2=opponent,
            chair=chair,
            roundNumber=round_number,
            judges=round_judges,
            gov=gov,
            winner=winner,
        )

        
        round_obj.speaks["team1"]["debater1"] = deb1_speaks
        round_obj.speaks["team1"]["debater2"] = deb2_speaks
        round_obj.ranks["team1"]["debater1"] = deb1_ranks
        round_obj.ranks["team1"]["debater2"] = deb2_ranks
        
        rounds[id] = round_obj
        team.rounds.append(round_obj)
    
    return {
        "teams": teams,
        "debaters": debaters,
        "judges": judges,
        "rounds": list(rounds.values()),
    }
