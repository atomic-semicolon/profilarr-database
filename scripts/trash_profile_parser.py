import argparse
import json
import sys
from pathlib import Path
import yaml
from constants import *

def load_template(template_path):
    """Load a YAML template file."""
    try:
        with open(template_path, 'r') as template_file:
            return yaml.safe_load(template_file)
    except FileNotFoundError:
        print(f"Error: Template file not found: {template_path}")
        sys.exit(1)

def sanitise_filename(name):
    replacements = str.maketrans(TEXT_REPLACEMENTS)
    return str(name).translate(replacements)

def write_regex_pattern_file(template_directory, regex_pattern_directory, regex_pattern_name, regex_pattern):
    regex_pattern_filename = sanitise_filename(f"(TRaSH) {regex_pattern_name}")
    regex_template = load_template(template_directory / "regexPattern.yml")
    regex_template['name'] = regex_pattern_filename
    regex_template['description'] = ''
    regex_template['pattern'] = regex_pattern
    regex_template['tags'] = [ 'TRaSH' ]
    regex_template['tests'] = []

    with open(regex_pattern_directory / f"{regex_pattern_filename}.yml", 'w') as regex_pattern_file:
        yaml.dump(regex_template,
                  regex_pattern_file,
                  sort_keys=False,
                  default_flow_style=False,
                  indent=2)
        
def get_custom_format_description(descriptions_directory, custom_format_filename):
    filename = Path(custom_format_filename).stem
    description = filename
    description_lines = []
    
    try:
        with open(descriptions_directory / f"{filename}.md", 'r') as custom_format_description_file:
            for index, line in enumerate(custom_format_description_file):
                # TRaSH Guide descriptions only start on line 4
                if index < 3:
                    continue
                if line.lstrip().startswith('<!--'):
                    break
                description_lines.append(line.rstrip('\n'))
        description = '\n'.join(description_lines)
    except FileNotFoundError:
        print(f"Warning: Description file not found for custom format {filename}")
    
    return description

def set_quality_id(quality, index):
    if QUALITIES.get(quality['name']):
        quality['id'] = QUALITIES[quality['name']]
        return index
    return index - 1

def main():
    parser = argparse.ArgumentParser(description='Create Dictionarry database entries for TRaSH guides')
    parser.add_argument('json_file', help='Input JSON file containing profile information')

    args = parser.parse_args()
    
    # Setup paths
    script_dir = Path(__file__).parent
    regex_dir = script_dir.parent / "regex_patterns"
    format_dir = script_dir.parent / "custom_formats"
    profile_dir = script_dir.parent / "profiles"
    template_dir = script_dir.parent / "templates"
    
    # TRaSH paths
    # docs/json/sonarr/quality-profiles/*.json
    source_dir = Path(args.json_file).parent.parent
    custom_formats_dir = source_dir / "cf"
    custom_format_descriptions_dir = source_dir.parent.parent.parent / "includes" / "cf-descriptions"
    
    # Load and parse input JSON
    try:
        with open(args.json_file, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: Input JSON file not found: {args.json_file}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON file: {args.json_file}")
        sys.exit(1)
        
    # Load template
    profile_filename = sanitise_filename(f"(TRaSH) {data['name']}")
    profile_template = load_template(template_dir / "profile.yml")
    profile_template['name'] = profile_filename
    profile_template['description'] = f"{str(data['trash_description']).replace('<br>', '\n')}"
    profile_template['tags'] = ["TRaSH"]
    profile_template['upgradesAllowed'] = data['upgradeAllowed']
    profile_template['minCustomFormatScore'] = data['minFormatScore']
    profile_template['upgradeUntilScore'] = data['cutoffFormatScore']
    profile_template['minScoreIncrement'] = data['minUpgradeFormatScore']
    profile_template['language'] = "must-original"
    
    print(f"Creating {profile_filename} profile...")
    
    # Setup qualities
    # Use mapping IDs provided
    # Create a negative index for quality groups (or unknown qualities)
    profile_template['qualities'] = []
    quality_group_index = -1
    for quality in data['items']:
        if quality.get('allowed'):
            quality_entry = {
                'id': 0,
                'name': quality['name']
            }
            
            quality_group_index = set_quality_id(quality_entry, quality_group_index)

            # Quality groups
            if quality.get('items'):
                quality_entry['qualities'] = []
                for sub_quality in quality['items']:
                    sub_quality_entry = {
                        'id': 0,
                        'name': sub_quality
                    }
                    
                    quality_group_index = set_quality_id(sub_quality_entry, quality_group_index)
                        
                    quality_entry['qualities'].append(sub_quality_entry)

            # Set 'upgrade until' value
            if quality['name'] == data['cutoff']:
                profile_template['upgrade_until'] = {
                    'id': quality_entry['id'],
                    'name': quality_entry['name']
                }
            
            profile_template['qualities'].append(quality_entry)
            
    # Set up regex patterns and custom formats
    # Make sure to run trash_custom_format_id_mapper before this
    with open(f"{script_dir}/trash-cf-mapping.json", 'r') as cf_mapping_file:
        cf_mapping = json.load(cf_mapping_file)
    
    profile_template['custom_formats'] = []
    for format_name in data['formatItems']:
        custom_format_filename = sanitise_filename(f"(TRaSH) {format_name}")
        custom_format_entry = {
            'name': custom_format_filename,
            'score': 0
        }
        
        cf_file_path = cf_mapping[data['formatItems'][format_name]]
        with open(f"{custom_formats_dir}/{cf_file_path}") as cf_file:
            custom_format = json.load(cf_file)
        
        profile_score_set = default_score_set = "default"
        if data.get('trash_score_set', {}):
            profile_score_set = data['trash_score_set']
            
        # Use profile score set, fallback to default, last resort zero score
        if custom_format.get('trash_scores', {}).get(profile_score_set, {}):
            custom_format_entry['score'] = custom_format['trash_scores'][profile_score_set]
        elif custom_format.get('trash_scores', {}).get(default_score_set, {}):
            custom_format_entry['score'] = custom_format['trash_scores'][default_score_set]
        
        # Create custom format file YML
        custom_format_template = load_template(template_dir / "customFormat.yml")
        custom_format_template['name'] = custom_format_filename
        custom_format_template['description'] = get_custom_format_description(custom_format_descriptions_dir, cf_file_path)
        custom_format_template['tags'] = [ 'TRaSH' ]
        custom_format_template['tests'] = []
        
        custom_format_conditions = []
        
        for specification in custom_format['specifications']:
            condition = {
                'name': f"(TRaSH) {specification['name']}",
                'type': CONDITION_TYPE[specification['implementation']],
                'required': specification['required'],
                'negate': specification['negate']
            }
            
            match condition['type']:
                case 'source':
                    condition['source'] = SOURCE_TYPE[specification['name']]
                case 'language':
                    condition['language'] = LANGUAGE[specification['fields']['value']]
                    # TODO: Double-check the purpose of exceptLanguage
                    condition['exceptLanguage'] = 'false'
                case 'release_title' | 'release_group':
                    condition['pattern'] = condition['name']

                    # Add a regex pattern file for the given condition
                    write_regex_pattern_file(template_dir, 
                                             regex_dir, 
                                             specification['name'], 
                                             specification['fields']['value'])
            
            custom_format_conditions.append(condition)
            
        custom_format_template['conditions'] = custom_format_conditions

        with open(format_dir / f"{custom_format_filename}.yml", 'w') as custom_format_file:
            yaml.dump(custom_format_template, 
                      custom_format_file,
                      sort_keys=False,
                      default_flow_style=False,
                      indent=2)
        
        profile_template['custom_formats'].append(custom_format_entry)
    
    with open(profile_dir / f"{profile_filename}.yml", 'w') as profile_file:
        yaml.dump(profile_template,
                  profile_file,
                  sort_keys=False,
                  default_flow_style=False,
                  indent=2)
    
if __name__ == "__main__":
    main()