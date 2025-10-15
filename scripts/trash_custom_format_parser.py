import argparse
import json
import os
import re
from glob import glob

from colorama import init

from common import *

init(strip=False, autoreset=True)

def parse_custom_format_description(custom_format_description_file):
    description_lines = []
    for line in custom_format_description_file:
        # Remove markdown linters and header lines
        if line.lstrip().startswith(('<!--', '**')):
            continue
        if line.rstrip():
            description_lines.append(line.rstrip())

    # Remove unused markdown properties
    return re.sub(r'''{[!:].*!?}''', '', '\n'.join(description_lines))

def get_custom_format_description(descriptions_directory, custom_format_filepath, target_app):
    filename = Path(custom_format_filepath).stem
    description = filename

    try:
        with open(descriptions_directory / f"{filename}.md", 'r') as custom_format_description_file:
            description = parse_custom_format_description(custom_format_description_file)
    except FileNotFoundError:
        # Some custom formats have different descriptions based on the target app
        try:
            filename += f"-{get_target_app_name(target_app)}"
            with open(descriptions_directory / f"{filename}.md", 'r') as custom_format_description_file:
                description = parse_custom_format_description(custom_format_description_file)
        except FileNotFoundError:
            print(Fore.YELLOW + f"Warning: Description file not found for custom format {filename}")

    # Some custom formats have an additional warning statement
    custom_format_warning_description_filepath = descriptions_directory / f"{filename}-warning.md"
    if os.path.exists(custom_format_warning_description_filepath):
        with open(custom_format_warning_description_filepath, 'r') as custom_format_warning_description_file:
            description += parse_custom_format_description(custom_format_warning_description_file)

    return description

def write_regex_pattern_file(regex_pattern_name, regex_pattern):
    # Try opening the regex file if it already exists
    # Add the newly found pattern as an alternative, and merge the rest of the information
    # TRaSH JSON files store the regex pattern pre-escaped, so they must be processed before saving in Profilarr
    regex_pattern_filename = sanitise_filename(f"{regex_pattern_name}")
    regex_template = load_template(TEMPLATE_PATH / "regexPattern.yml")
    regex_template['name'] = regex_pattern_filename
    regex_template['description'] = ''
    regex_template['pattern'] = regex_pattern
    regex_template['tags'] = ['TRaSH']
    regex_template['tests'] = []

    try:
        with open(REGEX_PATH / f"{regex_pattern_filename}.yml", 'r+') as regex_pattern_file:
            regex_pattern_data = yaml.load(regex_pattern_file, Loader=yaml.SafeLoader)
            if regex_template['pattern'] not in regex_pattern_data['pattern']:
                regex_pattern_data['pattern'] += f"|{regex_template['pattern']}"
            if 'TRaSH' not in regex_pattern_data['tags']:
                regex_pattern_data['tags'].append('TRaSH')

            # Re-save the file
            regex_pattern_file.seek(0)
            regex_pattern_file.truncate()
            yaml.dump(regex_pattern_data,
                      regex_pattern_file,
                      sort_keys=False,
                      default_flow_style=False,
                      indent=2)

    except FileNotFoundError:
        with open(REGEX_PATH / f"{regex_pattern_filename}.yml", 'w') as regex_pattern_file:
            yaml.dump(regex_template,
                      regex_pattern_file,
                      sort_keys=False,
                      default_flow_style=False,
                      indent=2)

def process_custom_formats_in_directory(trash_custom_formats_directory, trash_custom_format_descriptions_directory, target_app):
    for trash_custom_format_filepath in glob(f"{trash_custom_formats_directory}/*.json"):
        with open(trash_custom_format_filepath, "r") as trash_custom_format_file:
            trash_custom_format = json.load(trash_custom_format_file)
        custom_format_filename = sanitise_filename(f"{get_filename_prefix(target_app)}{trash_custom_format['name']}")

        custom_format = load_template(TEMPLATE_PATH / "customFormat.yml")
        custom_format['name'] = custom_format_filename
        custom_format['description'] = get_custom_format_description(trash_custom_format_descriptions_directory,
                                                                     trash_custom_format_filepath,
                                                                     target_app)
        custom_format['tags'] = ['TRaSH', f"{get_target_app_name(target_app).title()} Only"]
        custom_format['conditions'] = []
        custom_format['tests'] = []

        for specification in trash_custom_format['specifications']:
            condition = {
                'name': specification['name'],
                'type': CONDITION_TYPES[specification['implementation']],
                'required': specification['required'],
                'negate': specification['negate']
            }

            match condition['type']:
                case 'quality_modifier':
                    condition['qualityModifier'] = QUALITY_MODIFIERS[specification['fields']['value']]
                case 'resolution':
                    condition['resolution'] = f"{specification['fields']['value']}p"
                case 'source':
                    match target_app:
                        case TargetApp.RADARR:
                            condition['source'] = SOURCE_TYPES_RADARR[specification['fields']['value']]
                        case TargetApp.SONARR:
                            condition['source'] = SOURCE_TYPES_SONARR[specification['fields']['value']]
                case 'language':
                    match target_app:
                        case TargetApp.RADARR:
                            condition['language'] = LANGUAGES_RADARR[specification['fields']['value']]
                        case TargetApp.SONARR:
                            condition['language'] = LANGUAGES_SONARR[specification['fields']['value']]
                    # exceptLanguage does not have many uses (supposedly)
                    # Mainly seems to denote "every other language except this one"
                    # TRaSH mostly covers this using the 'negate' key, so defaulting this to false
                    condition['exceptLanguage'] = False
                case 'release_title' | 'release_group':
                    condition['pattern'] = condition['name']
                    write_regex_pattern_file(specification['name'], specification['fields']['value'])
                case 'release_type':
                    condition['releaseType'] = RELEASE_TYPES[specification['fields']['value']]
                case 'indexer_flag':
                    match target_app:
                        case TargetApp.RADARR:
                            condition['indexerFlag'] = INDEXER_FLAGS_RADARR[specification['fields']['value']]
                        case TargetApp.SONARR:
                            condition['indexerFlag'] = INDEXER_FLAGS_SONARR[specification['fields']['value']]

            custom_format['conditions'].append(condition)

        with open(FORMAT_PATH / f"{custom_format_filename}.yml", 'w') as custom_format_file:
            yaml.dump(custom_format,
                      custom_format_file,
                      sort_keys=False,
                      default_flow_style=False,
                      indent=2)

        print(Fore.GREEN + f"Processed: {custom_format_filename}")

def main():
    parser = argparse.ArgumentParser(description='Create TRaSH Guide custom format files for Dictionarry')
    parser.add_argument('trash_directory', help='Input TRaSH guides repository directory')
    args = parser.parse_args()

    # Setup internal path
    # This file should be under <repository folder>/scripts
    script_dir = Path(__file__).parent

    # Setup TRaSH paths
    trash_sonarr_custom_formats_dir = Path(args.trash_directory) / "docs" / "json" / get_target_app_name(TargetApp.SONARR) / "cf"
    trash_radarr_custom_formats_dir = Path(args.trash_directory) / "docs" / "json" / get_target_app_name(TargetApp.RADARR) / "cf"
    trash_custom_format_descriptions_dir = Path(args.trash_directory) / "includes" / "cf-descriptions"

    print(Fore.CYAN + "Processing Sonarr custom formats...")
    process_custom_formats_in_directory(trash_sonarr_custom_formats_dir, trash_custom_format_descriptions_dir, TargetApp.SONARR)
    print(Fore.CYAN + "Processing Radarr custom formats...")
    process_custom_formats_in_directory(trash_radarr_custom_formats_dir, trash_custom_format_descriptions_dir, TargetApp.RADARR)

if __name__ == "__main__":
    main()