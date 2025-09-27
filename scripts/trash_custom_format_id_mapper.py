import argparse
import ijson
import json
import os
from glob import glob
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Create ')
    parser.add_argument('custom_format_directory', help='Directory of the TRaSH custom formats')

    args = parser.parse_args()

    # Create JSON
    mapping = {}
    for file_path in glob(f"{args.custom_format_directory}/*.json"):
        with open(file_path, 'r') as cf_file:
            for trash_id in ijson.items(cf_file, 'trash_id'):
                mapping[trash_id] = os.path.basename(file_path)
                break
    
    # Write JSON to file
    with open(f"{Path(__file__).parent}/trash-cf-mapping.json", 'w') as cf_mapping_file:
        json.dump(mapping, cf_mapping_file)
    
if __name__ == "__main__":
    main()