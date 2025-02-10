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
                debaters[deb1_name] = Debater(name=deb1_name, isVarsity=deb1_status)
            if deb2_name not in debaters:
                debaters[deb2_name] = Debater(name=deb2_name,  isVarsity=deb2_status)
            
            if team_name not in teams:
                teams[team_name] = Team(name=team_name, debater1=debaters[deb1_name], debater2=debaters[deb2_name])
            if opponent_name not in teams:
                teams[opponent_name] = Team(name=opponent_name, debater1=None, debater2=None)
            
            if chair_name not in judges:
                judges[chair_name] = Judge(name=chair_name)
            for wing in wings:
                if wing not in judges:
                    judges[wing] = Judge(name=wing)
            
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


def write_csv(filepath, data):
    teams = data["teams"]
    rounds = data["rounds"]
    
    header = [
        "Round id", "Round", "Gov/Opp", "Win/Loss", "Team Name", "Opponent", 
        "Chair", "Wing(s)", "Debater 1", "Debater 2", "N/V", "Speaks", "Ranks"
    ]
    
    with open(filepath, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        
        for round_obj in rounds:
            team = round_obj.team1
            opponent = round_obj.team2
            chair = round_obj.chair
            wings = " - ".join(judge.name for judge in round_obj.judges)
            
            deb1 = team.debater1
            deb2 = team.debater2
            
            deb1_speaks = round_obj.speaks["team1"]["debater1"]
            deb2_speaks = round_obj.speaks["team1"]["debater2"]
            deb1_ranks = round_obj.ranks["team1"]["debater1"]
            deb2_ranks = round_obj.ranks["team1"]["debater2"]
            
            row = [
                round_obj.id,
                round_obj.roundNumber,
                "G" if round_obj.gov else "O",
                "W" if round_obj.winner else "L",
                team.name,
                opponent.name,
                chair.name,
                wings,
                deb1.name,
                deb2.name,
                "V" if deb1.isVarsity and deb2.isVarsity else "N",
                deb1_speaks,
                deb1_ranks,
            ]
            
            writer.writerow(row)
