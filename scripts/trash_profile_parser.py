import argparse
import json
from glob import glob

from colorama import init

from common import *

# Colorama setup
init(strip=False, autoreset=True)

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

def normalise_quality_name(quality_name):
    if quality_name == "Bluray-1080p Remux":
        return "Remux-1080p"
    if quality_name == "Bluray-2160p Remux":
        return "Remux-2160p"
    return quality_name

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
                        'name': normalise_quality_name(sub_quality)
                    }

                    quality_entry['qualities'].append(sub_quality_entry)

                quality_entry['id'] = quality_group_index
                quality_group_index -= 1
            else:
                # If it's not a quality group, it MUST have an associated ID
                quality_entry['id'] = QUALITIES[normalise_quality_name(quality['name'])]

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

    for trash_custom_format_name in trash_quality_profile['formatItems']:
        custom_format_filename = sanitise_filename(f"{get_filename_prefix(target_app)}{trash_custom_format_name}")

        # Initialise the entry that will be in the quality profile
        custom_format_entry = {
            'name': custom_format_filename,
            'score': 0
        }

        # Map to the custom format files already created
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