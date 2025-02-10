import os
import shutil
import json
import xml.etree.ElementTree as ET
import csv
from debate_archive_tools import *
from JSON import deserialize_json
from CSV import parse_csv
from XML import ArchiveParser


def read_data(file, filetype):
    """ Reads data from a given file and returns a comparable dictionary. """
    if filetype == "json":
        return deserialize_json(file)
    elif filetype == "csv":
        return parse_csv(file)
    elif filetype == "xml":
        parser = ArchiveParser(file)
        parser.parse()
        return parser.get_parsed_data()
    else:
        raise ValueError(f"Unsupported file type: {filetype}")


def compare_data(original_data, converted_data):
    
    def find_by_name(collection, name):
        return next((item for item in collection if item.name == name), None)

    def find_by_id(collection, entity_id):
        return next((item for item in collection if item.id == entity_id), None)

    def compare_fields(label, original, converted, fields):
        for field in fields:
            orig_value = getattr(original, field, None)
            conv_value = getattr(converted, field, None)
            if orig_value != conv_value:
                print(f"Difference in {label} '{original.name}' - Field '{field}': {orig_value} vs {conv_value}")

    # Compare teams
    for orig_team in original_data["teams"]:
        conv_team = find_by_name(converted_data["teams"], orig_team.name)
        if not conv_team:
            print(f"Missing team in converted data: {orig_team.name}")
        else:
            compare_fields("Team", orig_team, conv_team, ["id"])

            # Compare debaters in the team
            for orig_debater in [orig_team.debater1, orig_team.debater2]:
                if orig_debater:
                    conv_debater = find_by_name([conv_team.debater1, conv_team.debater2], orig_debater.name)
                    if not conv_debater:
                        print(f"Missing debater in converted data: {orig_debater.name}")
                    else:
                        compare_fields("Debater", orig_debater, conv_debater, ["id", "isVarsity"])

    # Compare debaters
    for orig_debater in original_data["debaters"]:
        conv_debater = find_by_name(converted_data["debaters"], orig_debater.name)
        if not conv_debater:
            print(f"Missing debater in converted data: {orig_debater.name}")
        else:
            compare_fields("Debater", orig_debater, conv_debater, ["id", "isVarsity"])

    # Compare judges
    for orig_judge in original_data["judges"]:
        conv_judge = find_by_name(converted_data["judges"], orig_judge.name)
        if not conv_judge:
            print(f"Missing judge in converted data: {orig_judge.name}")
        else:
            compare_fields("Judge", orig_judge, conv_judge, ["id"])

    # Compare rounds
    for orig_round in original_data["rounds"]:
        conv_round = find_by_id(converted_data["rounds"], orig_round.id)
        if not conv_round:
            print(f"Missing round in converted data: ID {orig_round.id}")
        else:
            compare_fields("Round", orig_round, conv_round, ["name", "roundNumber", "winner", "gov"])

            # Compare teams in rounds
            for team_role in ["team1", "team2"]:
                orig_team = getattr(orig_round, team_role, None)
                if orig_team:
                    conv_team = find_by_name([conv_round.team1, conv_round.team2], orig_team.name) if conv_round else None
                    if not conv_team:
                        print(f"Missing {team_role} in round {orig_round.id}: {orig_team.name}")
                    else:
                        compare_fields(f"Round {orig_round.id} {team_role}", orig_team, conv_team, ["id"])

            # Compare judges
            for orig_judge in orig_round.judges:
                conv_judge = find_by_name(conv_round.judges, orig_judge.name) if conv_round else None
                if not conv_judge:
                    print(f"Missing judge in round {orig_round.id}: {orig_judge.name}")

            # Compare rankings and speaks
            for team_key in ["team1", "team2"]:
                for debater_key in ["debater1", "debater2"]:
                    orig_rank = orig_round.ranks[team_key].get(debater_key, "")
                    conv_rank = conv_round.ranks[team_key].get(debater_key, "") if conv_round else None
                    if orig_rank != conv_rank:
                        print(f"Rank difference in round {orig_round.id}, {team_key} {debater_key}: {orig_rank} vs {conv_rank}")

                    orig_speak = orig_round.speaks[team_key].get(debater_key, "")
                    conv_speak = conv_round.speaks[team_key].get(debater_key, "") if conv_round else None
                    if orig_speak != conv_speak:
                        print(f"Speak difference in round {orig_round.id}, {team_key} {debater_key}: {orig_speak} vs {conv_speak}")

    print("Comparison complete.")



def run_tests():
    filetypes = ["csv", "json", "xml"]
    input_files = {ft: f"test.{ft}" for ft in filetypes}

    for input_type in filetypes:
        input_file = input_files[input_type]
        try:
            original_data = read_data(input_file, input_type)
        except Exception as e:
            print(f"Error reading {input_type} file: {e}")
            continue

        for output_type in filetypes:
            
            output_file = f"converted.{output_type}"

            os.system(f"python debate_archive_tools.py {input_file} {output_type} --output {output_file}")

            try:
                converted_data = read_data(output_file, output_type)
            except Exception as e:
                print(f"Error reading converted {output_type} file: {e}")
                continue

            print(f"Comparing {input_type} -> {output_type}")
            try:
                compare_data(original_data, converted_data)
            except Exception as e:
                print(f"Error during comparison: {e}")
                
            os.remove(output_file)


if __name__ == "__main__":
    run_tests()
