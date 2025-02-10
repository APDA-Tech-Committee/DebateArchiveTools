import csv
from models import *

GOV = "G"
OPP = "O"


def get_victor_label(victor_code, side):
    side = 0 if side == GOV else 1
    victor_map = {
        0: ("", ""),
        1: ("W", "L"),
        2: ("L", "W"),
        3: ("WF", "LF"),
        4: ("LF", "WF"),
        5: ("AD", "AD"),
        6: ("AW", "AW"),
    }
    return victor_map[victor_code][side]


def parse_csv(filepath):
    teams = {}
    debaters = {}
    judges = {}
    rounds = []
    
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        #ignore header
        next(reader)

        for row in reader:
            if row["Round"] == "Total" or row["Round"] is None:
                continue
            team_name = row["Team Name"]
            school = row["School"]
            round_number = int(row["Round"])
            gov_opp = row["Gov/Opp"]
            win_loss = row["Win/Loss"]
            opponent_name = row["Opponent"]
            chair_name = row["Chair"]
            wings = row["Wing(s)"].split(" - ") if row["Wing(s)"] else []
            
            deb1_name = row["Debater 1"]
            deb1_status = row["N/V"] == "V"
            deb1_speaks = float(row["Speaks"])
            deb1_ranks = float(row["Ranks"])
            
            deb2_name = row["Debater 2"]
            deb2_status = row["N/V"] == "V"
            deb2_speaks = float(row["Speaks"])
            deb2_ranks = float(row["Ranks"])
            
            # Create debaters if not exists
            if deb1_name not in debaters:
                debaters[deb1_name] = Debater(deb1_name, deb1_name, deb1_status)
            if deb2_name not in debaters:
                debaters[deb2_name] = Debater(deb2_name, deb2_name, deb2_status)
            
            deb1 = debaters[deb1_name]
            deb2 = debaters[deb2_name]
            
            # Create team if not exists
            if team_name not in teams:
                teams[team_name] = Team(team_name, team_name, deb1, deb2)
            team = teams[team_name]
            
            # Create judge if not exists
            if chair_name not in judges:
                judges[chair_name] = Judge(chair_name, chair_name)
            chair = judges[chair_name]
            
            # Process wings (assistant judges)
            round_judges = [chair]
            for wing in wings:
                if wing not in judges:
                    judges[wing] = Judge(wing, wing)
                round_judges.append(judges[wing])
                
            # Create opponent team if not exists
            if opponent_name not in teams:
                teams[opponent_name] = Team(opponent_name, opponent_name, None, None)
            opponent = teams[opponent_name]
            
            # Create round
            round_obj = Round(round_number, f"Round {round_number}", team, opponent, chair, roundNumber=round_number)
            round_obj.judges = round_judges
            
            # Assign results
            
            round_obj.speaks["team1"]["debater1"] = deb1_speaks
            round_obj.speaks["team1"]["debater2"] = deb2_speaks
            round_obj.ranks["team1"]["debater1"] = deb1_ranks
            round_obj.ranks["team1"]["debater2"] = deb2_ranks
            
            rounds.append(round_obj)
            team.rounds.append(round_obj)
    
    return {
            "teams": teams,
            "debaters": debaters,
            "judges": judges,
            "rounds": rounds
        }

