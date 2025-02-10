import argparse, os, sys
import xml.etree.ElementTree as ET
from models import *
from XML import ArchiveParser
from JSON import deserialize_json
from CSV import parse_csv
import haikunator



def main():
    parser = argparse.ArgumentParser(description='Process debate archive files.')
    parser.add_argument('filename', type=str, help='The name of the file to process')
    parser.add_argument('format', type=str, help='The format of the file (e.g., json, csv, xml)')
    
    args = parser.parse_args()
    
    filename = args.filename
    file_format = args.format
    
    print(f'Processing file: {filename} with format: {file_format}')
    
    input_format = os.path.splitext(filename)[1][1:].lower()
    if input_format == "xml":
        parser = ArchiveParser(filename)
        parser.parse()
        data = parser.get_parsed_data()
    
    elif input_format == "json":
        data = deserialize_json(filename)

    elif input_format == "csv":
         data = parse_csv(filename)
    
    print(data)

    for round in data["rounds"]:
            print(round.team1.debater1.name)

        

if __name__ == '__main__':
    main()