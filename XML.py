import xml.etree.ElementTree as ET
from models import *

class ArchiveParser:
    def __init__(self, filename):
        self.tree = ET.ElementTree(file=filename)
        self.root = self.tree.getroot()
        self.tournament_name = self.root.attrib.get("name", "Unknown Tournament")
        self.teams = {}
        self.debaters = {}
        self.judges = {}
        self.rounds = []

    def parse(self):
        self.parse_participants()
        self.parse_rounds()

    def parse_participants(self):
        participants_elem = self.root.find("participants")

        for team_elem in participants_elem.findall("team"):
            team_id = team_elem.attrib["id"]
            team_name = team_elem.attrib["name"]
            speakers = []

            for speaker_elem in team_elem.findall("speaker"):
                speaker_id = speaker_elem.attrib["id"]
                speaker_name = speaker_elem.text
                is_varsity = "varsity" in speaker_elem.attrib.get("categories", "").lower()
                debater = Debater(id=speaker_id, name=speaker_name, isVarsity=is_varsity)
                self.debaters[speaker_id] = debater
                speakers.append(debater)

            if len(speakers) == 2:
                self.teams[team_id] = Team(id=team_id, name=team_name, debater1=speakers[0], debater2=speakers[1])

        for adjudicator_elem in participants_elem.findall("adjudicator"):
            judge_id = adjudicator_elem.attrib["id"]
            judge_name = adjudicator_elem.attrib["name"]
            judge = Judge(id=judge_id, name=judge_name)
            self.judges[judge_id] = judge

    def parse_rounds(self):
        for round_elem in self.root.findall("round"):
            round_name = round_elem.attrib["name"]
            round_number = int(round_elem.attrib.get("number", 0))

            for debate_elem in round_elem.findall("debate"):
                debate_id = debate_elem.attrib["id"]
                chair_id = debate_elem.attrib.get("chair")
                chair = self.judges.get(chair_id) if chair_id in self.judges else None
                adjudicator_ids = debate_elem.attrib.get("adjudicators", "").split()
                judges = [self.judges[jid] for jid in adjudicator_ids if jid in self.judges]

                sides = {}
                for side_elem in debate_elem.findall("side"):
                    team_id = side_elem.attrib["team"]
                    team = self.teams.get(team_id)
                    if team:
                        sides[team_id] = team

                if len(sides) == 2:
                    team_ids = list(sides.keys())
                    round_obj = Round(id=debate_id, name=round_name, team1=sides[team_ids[0]], team2=sides[team_ids[1]], chair=chair, gov=True, roundNumber=round_number)
                    round_obj.judges = judges
                    first = True

                    for team_id, team in sides.items():
                        side_elem = next((s for s in debate_elem.findall("side") if s.attrib["team"] == team_id), None)
                        if side_elem:
                            if first:
                                first = False
                                outer_ballot_elem = side_elem.find("ballot")
                                if outer_ballot_elem is not None:
                                    rank = int(outer_ballot_elem.attrib.get("rank", 0))
                                    if rank == 1:
                                        round_obj.winner = True
                            
                            speech_elems = side_elem.findall("speech")
                            for speech_elem in speech_elems:
                                speaker_id = speech_elem.attrib["speaker"]
                                speaker = self.debaters.get(speaker_id)
                                if speaker:
                                    ballot_elem = speech_elem.find("ballot")
                                    if ballot_elem is not None:
                                        speaks = float(ballot_elem.text)
                                        rank = int(ballot_elem.attrib.get("rank", 0))
                                        if speaker == team.debater1:
                                            round_obj.speaks["team1"]["debater1"] = speaks
                                            round_obj.ranks["team1"]["debater1"] = rank
                                        elif speaker == team.debater2:
                                            round_obj.speaks["team1"]["debater2"] = speaks
                                            round_obj.ranks["team1"]["debater2"] = rank
                    
                    self.rounds.append(round_obj)
                    team.rounds.append(round_obj)

    def get_parsed_data(self):
        return {
            "teams": self.teams,
            "debaters": self.debaters,
            "judges": self.judges,
            "rounds": self.rounds
        }

class ArchiveGenerator:
    def __init__(self, teams, debaters, judges, rounds):
        self.tournament_name = "Generated Tournament"
        self.teams = teams
        self.debaters = debaters
        self.judges = judges
        self.rounds = rounds
    
    def generate_xml(self):
        root = ET.Element("tournament", name=self.tournament_name)
        participants_elem = ET.SubElement(root, "participants")
        
        for team in self.teams.values():
            team_elem = ET.SubElement(participants_elem, "team", id=team.id, name=team.name)
            
            for debater in [team.debater1, team.debater2]:
                categories = "varsity" if debater.isVarsity else ""
                speaker_elem = ET.SubElement(team_elem, "speaker", id=debater.id, categories=categories)
                speaker_elem.text = debater.name
        
        for judge in self.judges.values():
            ET.SubElement(participants_elem, "adjudicator", id=judge.id, name=judge.name)
        
        for round_obj in self.rounds:
            round_elem = ET.SubElement(root, "round", name=round_obj.name, number=str(round_obj.roundNumber))
            debate_elem = ET.SubElement(round_elem, "debate", id=round_obj.id, chair=round_obj.chair.id if round_obj.chair else "", 
                                       adjudicators=" ".join(j.id for j in round_obj.judges))
            
            for team_key, team in [("team1", round_obj.team1), ("team2", round_obj.team2)]:
                side_elem = ET.SubElement(debate_elem, "side", team=team.id)
                
                if team_key == "team1" and round_obj.winner:
                    ET.SubElement(side_elem, "ballot", rank="1")
                
                for debater_key, debater in [("debater1", team.debater1), ("debater2", team.debater2)]:
                    if debater:
                        speech_elem = ET.SubElement(side_elem, "speech", speaker=debater.id)
                        ballot_elem = ET.SubElement(speech_elem, "ballot", rank=str(round_obj.ranks[team_key][debater_key]))
                        ballot_elem.text = str(round_obj.speaks[team_key][debater_key])
        
        return ET.ElementTree(root)
    
    def save_to_file(self, filename):
        tree = self.generate_xml()
        tree.write(filename, encoding="utf-8", xml_declaration=True)
