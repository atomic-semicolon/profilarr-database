import argparse
import ijson
import json
import os
from glob import glob
from pathlib import Path
from constants import CUSTOM_FORMAT_MAPPING_FILENAME

def main():
    parser = argparse.ArgumentParser(description='Create a mapping from TRaSH custom format filenames to their IDs')
    parser.add_argument('trash_directory', help='Input TRaSH guides repository directory')
    args = parser.parse_args()

    # The trash_directory argument must point to the base folder of the TRaSH guides repository
    # Files (as of 08/10/2025) are located in:
    # docs/json/<app>/cf/*.json
    trash_sonarr_custom_formats_dir = Path(args.trash_directory) / "docs" / "json" / "sonarr" / "cf"
    trash_radarr_custom_formats_dir = Path(args.trash_directory) / "docs" / "json" / "radarr" / "cf"

    trash_custom_format_filepaths = glob(f"{trash_sonarr_custom_formats_dir}/*.json") + glob(f"{trash_radarr_custom_formats_dir}/*.json")

    # Create JSON
    mapping = {}
    for trash_custom_format_filepath in trash_custom_format_filepaths:
        with open(trash_custom_format_filepath, 'r') as trash_custom_format_file:
            for trash_id in ijson.items(trash_custom_format_file, 'trash_id'):
                mapping[trash_id] = os.path.basename(trash_custom_format_filepath)
                break
    
    # Write JSON to file
    with open(f"{Path(__file__).parent}/{CUSTOM_FORMAT_MAPPING_FILENAME}", 'w') as custom_format_mapping_file:
        json.dump(mapping, custom_format_mapping_file)
    
if __name__ == "__main__":
    main()