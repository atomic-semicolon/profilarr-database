import argparse
import json
import os.path
import re
import sys
import yaml
from constants import *
from glob import glob
from enum import Enum, auto
from colorama import Fore, init

# Colorama setup
init(autoreset=True)

class TargetApp(Enum):
    RADARR = auto()
    SONARR = auto()

def get_target_app_name(target_app):
    match target_app:
        case TargetApp.RADARR:
            return 'radarr'
        case TargetApp.SONARR:
            return 'sonarr'
    return ''

def load_template(template_path):
    """Load a YAML template file."""
    try:
        with open(template_path, 'r') as template_file:
            return yaml.safe_load(template_file)
    except FileNotFoundError:
        print(Fore.RED + f"Error: Template file not found: {template_path}")
        sys.exit(1)

def sanitise_filename(name):
    replacements = str.maketrans(TEXT_REPLACEMENTS)
    return str(name).translate(replacements)

def write_regex_pattern_file(regex_pattern_name, regex_pattern):
    # Try opening the regex file if it already exists
    # Add the newly found pattern as an alternative, and merge the rest of the information
    # TRaSH JSON files store the regex pattern pre-escaped, so they must be processed before saving in Profilarr
    regex_pattern_filename = sanitise_filename(f"{regex_pattern_name}")
    regex_template = load_template(TEMPLATE_PATH / "regexPattern.yml")
    regex_template['name'] = regex_pattern_filename
    regex_template['description'] = ''
    regex_template['pattern'] = regex_pattern
    regex_template['tags'] = [ 'TRaSH' ]
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

def parse_custom_format_description(custom_format_description_file):
    description_lines = []
    for index, line in enumerate(custom_format_description_file):
        # Remove markdown linters and header lines
        if line.lstrip().startswith(('<!--', '**')):
            continue
        if line.rstrip():
            description_lines.append(line.rstrip())

    # Remove unused markdown properties
    return re.sub(r'''{[!:].*!?}''', '', '\n'.join(description_lines))

def get_custom_format_description(descriptions_directory, custom_format_filename, target_app):
    filename = Path(custom_format_filename).stem
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

def initialise_profile_template(trash_quality_profile):
    profile_filename = sanitise_filename(f"(TRaSH) {trash_quality_profile['name']}")
    profile_template = load_template(TEMPLATE_PATH / "profile.yml")
    profile_template['name'] = profile_filename
    profile_template['description'] = f"{str(trash_quality_profile['trash_description']).replace('<br>', '\n')}"
    profile_template['tags'] = ["TRaSH"]
    profile_template['upgradesAllowed'] = trash_quality_profile['upgradeAllowed']
    profile_template['minCustomFormatScore'] = trash_quality_profile['minFormatScore']
    profile_template['upgradeUntilScore'] = trash_quality_profile['cutoffFormatScore']
    profile_template['minScoreIncrement'] = trash_quality_profile['minUpgradeFormatScore']
    profile_template['language'] = "must_original"
    profile_template['qualities'] = []
    profile_template['custom_formats'] = []
    profile_template['custom_formats_radarr'] = []
    profile_template['custom_formats_sonarr'] = []

    print(Fore.GREEN + f"Creating {profile_filename} profile...")
    return profile_template

def process_qualities_from_profile(trash_quality_profile, quality_profile):
    # Setup qualities using mapping IDs
    # Quality groups and unknown qualities have negative indices
    quality_group_index = -1
    for quality in trash_quality_profile['items']:
        if quality.get('allowed'):
            # Don't set the ID just yet
            quality_entry = {
                'name': quality['name']
            }

            # Quality groups
            # These don't have an associated ID, any negative integer works
            if quality.get('items'):
                quality_entry['qualities'] = []
                for sub_quality in quality['items']:
                    # Sub-quality is usually not a group, i.e. no nested quality groups
                    # ID should be set instantly
                    sub_quality_entry = {
                        'id': QUALITIES[sub_quality],
                        'name': sub_quality
                    }

                    quality_entry['qualities'].append(sub_quality_entry)

                quality_entry['id'] = quality_group_index
                quality_group_index -= 1
            else:
                # If it's not a quality group, it MUST have an associated ID
                quality_entry['id'] = QUALITIES[quality['name']]

            # Set 'upgrade until' value
            if quality['name'] == trash_quality_profile['cutoff']:
                quality_profile['upgrade_until'] = {
                    'id': quality_entry['id'],
                    'name': quality_entry['name']
                }

            # Add quality to the beginning of list
            # TRaSH Guides seem to put qualities in order of increasing favorability
            quality_profile['qualities'] = [quality_entry] + quality_profile['qualities']
            
    return quality_profile

def write_quality_profile_file(quality_profile):
    try:
        with open(PROFILE_PATH / f"{quality_profile['name']}.yml", 'r+') as quality_profile_file:
            quality_profile_data = yaml.safe_load(quality_profile_file)

            # Merge non-empty lists from the original file into the new one
            if quality_profile_data.get('custom_formats_sonarr', {}) and not quality_profile['custom_formats_sonarr']:
                quality_profile['custom_formats_sonarr'] += [x for x in quality_profile_data['custom_formats_sonarr'] if x not in quality_profile['custom_formats_sonarr']]
            if quality_profile_data.get('custom_formats_radarr', {}) and not quality_profile['custom_formats_radarr']:
                quality_profile['custom_formats_radarr'] += [x for x in quality_profile_data['custom_formats_radarr'] if x not in quality_profile['custom_formats_radarr']]
            if quality_profile_data.get('custom_formats', {}) and not quality_profile['custom_formats']:
                quality_profile['custom_formats'] += [x for x in quality_profile_data['custom_formats'] if x not in quality_profile['custom_formats']]

            # Find commonalities between the app-specific custom formats and merge them
            common_custom_formats = [x for x in quality_profile['custom_formats_sonarr'] if x in quality_profile['custom_formats_radarr']]
            quality_profile['custom_formats'] += [x for x in common_custom_formats if x not in quality_profile['custom_formats']]
            quality_profile['custom_formats_radarr'] = [x for x in quality_profile['custom_formats_radarr'] if x not in quality_profile['custom_formats']]
            quality_profile['custom_formats_sonarr'] = [x for x in quality_profile['custom_formats_sonarr'] if x not in quality_profile['custom_formats']]
            print(Fore.CYAN + f"Found formats - RADARR: {len(quality_profile['custom_formats_radarr'])} SONARR: {len(quality_profile['custom_formats_sonarr'])} COMMON: {len(quality_profile['custom_formats'])}")

            # Re-save the file
            quality_profile_file.seek(0)
            quality_profile_file.truncate()
            yaml.dump(quality_profile,
                      quality_profile_file,
                      sort_keys=False,
                      default_flow_style=False,
                      indent=2)

    except FileNotFoundError:
        with open(PROFILE_PATH / f"{quality_profile['name']}.yml", 'w') as quality_profile_file:
            yaml.dump(quality_profile,
                      quality_profile_file,
                      sort_keys=False,
                      default_flow_style=False,
                      indent=2)

def process_custom_formats(trash_quality_profile, trash_custom_format_mapping, trash_directory, quality_profile, target_app):
    trash_custom_formats_dir = trash_directory / "docs" / "json" / get_target_app_name(target_app) / "cf"
    trash_custom_format_descriptions_dir = trash_directory / "includes" / "cf-descriptions"
    
    for trash_custom_format_name in trash_quality_profile['formatItems']:
        custom_format_filename = sanitise_filename(f"(TRaSH) {trash_custom_format_name}")
        custom_format_entry = {
            'name': custom_format_filename,
            'score': 0
        }
        
        trash_custom_format_filename = trash_custom_format_mapping[trash_quality_profile['formatItems'][trash_custom_format_name]]
        with open(f"{trash_custom_formats_dir}/{trash_custom_format_filename}", 'r') as trash_custom_format_file:
            trash_custom_format = json.load(trash_custom_format_file)

        profile_score_set = default_score_set = "default"
        if trash_quality_profile.get('trash_score_set', {}):
            profile_score_set = trash_quality_profile['trash_score_set']

        # Use profile score set, fallback to default
        # Leave a default score of zero as a last resort
        if trash_custom_format.get('trash_scores', {}).get(profile_score_set, {}):
            custom_format_entry['score'] = trash_custom_format['trash_scores'][profile_score_set]
        elif trash_custom_format.get('trash_scores', {}).get(default_score_set, {}):
            custom_format_entry['score'] = trash_custom_format['trash_scores'][default_score_set]
        
        custom_format = load_template(TEMPLATE_PATH / "customFormat.yml")
        custom_format['name'] = custom_format_filename
        custom_format['description'] = get_custom_format_description(trash_custom_format_descriptions_dir, trash_custom_format_filename, target_app)
        custom_format['tags'] = [ 'TRaSH' ]
        custom_format['conditions'] = []
        custom_format['tests'] = []

        for specification in trash_custom_format['specifications']:
            condition = {
                'name': specification['name'],
                'type': CONDITION_TYPE[specification['implementation']],
                'required': specification['required'],
                'negate': specification['negate']
            }

            match condition['type']:
                case 'quality_modifier':
                    condition['qualityModifier'] = QUALITY_MODIFIER[specification['fields']['value']]
                case 'resolution':
                    condition['resolution'] = f"{specification['fields']['value']}p"
                case 'source':
                    if specification['name'].lower().startswith('not'):
                        # Handle "not <quality>" cases
                        condition['source'] = SOURCE_TYPE[specification['name'][4:].lower()]
                    else:
                        condition['source'] = SOURCE_TYPE[specification['name'].lower()]
                case 'language':
                    condition['language'] = LANGUAGE[specification['fields']['value']]
                    # TODO: Double-check the purpose of exceptLanguage
                    condition['exceptLanguage'] = 'false'
                case 'release_title' | 'release_group':
                    condition['pattern'] = condition['name']

                    # Add a regex pattern file for the given condition
                    write_regex_pattern_file(specification['name'],
                                             specification['fields']['value'])

            custom_format['conditions'].append(condition)

        with open(FORMAT_PATH / f"{custom_format_filename}.yml", 'w') as custom_format_file:
            yaml.dump(custom_format,
                      custom_format_file,
                      sort_keys=False,
                      default_flow_style=False,
                      indent=2)

        match target_app:
            case TargetApp.RADARR:
                quality_profile['custom_formats_radarr'].append(custom_format_entry)
            case TargetApp.SONARR:
                quality_profile['custom_formats_sonarr'].append(custom_format_entry)
        
    return quality_profile

def process_quality_profiles(trash_quality_profiles_dir, trash_custom_format_mapping, trash_directory, target_app):
    for trash_quality_profile_filepath in glob(f"{trash_quality_profiles_dir}/*.json"):
        with open(trash_quality_profile_filepath, 'r') as trash_quality_profile_file:
            trash_quality_profile = json.load(trash_quality_profile_file)

        quality_profile = initialise_profile_template(trash_quality_profile)
        quality_profile = process_qualities_from_profile(trash_quality_profile, quality_profile)
        quality_profile = process_custom_formats(trash_quality_profile,
                                                 trash_custom_format_mapping,
                                                 trash_directory,
                                                 quality_profile,
                                                 target_app)

        write_quality_profile_file(quality_profile)

def main():
    parser = argparse.ArgumentParser(description='Create Dictionarry database entries for TRaSH guides')
    parser.add_argument('trash_directory', help='Input TRaSH guides repository directory')
    args = parser.parse_args()

    # Setup internal path
    # This file should be under <repository folder>/scripts
    script_dir = Path(__file__).parent

    # Make sure to run trash_custom_format_id_mapper.py before this
    try:
        with open(f"{script_dir}/{CUSTOM_FORMAT_MAPPING_FILENAME}", 'r') as trash_custom_format_mapping_file:
            trash_custom_format_mapping = json.load(trash_custom_format_mapping_file)
    except FileNotFoundError:
        print(Fore.RED + "Error: Please run trash_custom_format_id_mapper.py first")
        sys.exit(1)
    
    # Setup TRaSH guides folders
    # The trash_directory argument must point to the base folder of the TRaSH guides repository
    # Files (as of 08/10/2025) are located in:
    # docs/json/<app>/quality-profiles/*.json
    trash_radarr_quality_profiles_dir = Path(args.trash_directory) / "docs" / "json" / "radarr" / "quality-profiles"
    trash_sonarr_quality_profiles_dir = Path(args.trash_directory) / "docs" / "json" / "sonarr" / "quality-profiles"

    process_quality_profiles(trash_radarr_quality_profiles_dir, trash_custom_format_mapping, Path(args.trash_directory), TargetApp.RADARR)
    process_quality_profiles(trash_sonarr_quality_profiles_dir, trash_custom_format_mapping, Path(args.trash_directory), TargetApp.SONARR)

if __name__ == "__main__":
    main()