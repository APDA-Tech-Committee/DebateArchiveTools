import argparse, os, sys
import xml.etree.ElementTree as ET
from models import *
from XML import ArchiveParser, ArchiveGenerator
from JSON import deserialize_json, serialize_json
from CSV import parse_csv, write_csv
import haikunator

def main():
    parser = argparse.ArgumentParser(description='Process debate archive files.')
    parser.add_argument('filename', type=str, help='The name of the file to process')
    parser.add_argument('format', type=str, help='The format of the file (e.g., json, csv, xml)')
    parser.add_argument('--output', type=str, help='The name of the output file (optional)')
    
    args = parser.parse_args()
    
    filename = args.filename
    output_format = args.format.lower()
    output_filename = args.output
    
    if not output_filename:
        output_filename = "converted."+os.path.splitext(filename)[0] + '.' + output_format
    
    print(f'Converting: {filename} to {output_format}')
    
    input_format = os.path.splitext(filename)[1][1:].lower()
    if input_format == "xml":
        parser = ArchiveParser(filename)
        parser.parse()
        data = parser.get_parsed_data()
    elif input_format == "json":
        data = deserialize_json(filename)
    elif input_format == "csv":
        data = parse_csv(filename)
    
    if output_format == "xml":
        writer = ArchiveGenerator(*data.values())
        writer.generate_xml()
        writer.save_to_file(output_filename)
    elif output_format == "json":
        serialize_json(output_filename, data)
    elif output_format == "csv":
        write_csv(output_filename, data)

if __name__ == '__main__':
    main()