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
                debater = Debater(speaker_id, speaker_name, is_varsity)
                self.debaters[speaker_id] = debater
                speakers.append(debater)

            if len(speakers) == 2:
                self.teams[team_id] = Team(team_id, team_name, speakers[0], speakers[1])

        for adjudicator_elem in participants_elem.findall("adjudicator"):
            judge_id = adjudicator_elem.attrib["id"]
            judge_name = adjudicator_elem.attrib["name"]
            judge = Judge(judge_id, judge_name)
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
                    round_obj = Round(debate_id, round_name, sides[team_ids[0]], sides[team_ids[1]], chair, round_number)
                    round_obj.judges = judges
                    
                    for team_id, team in sides.items():
                        side_elem = next((s for s in debate_elem.findall("side") if s.attrib["team"] == team_id), None)
                        if side_elem:
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
