import argparse
import json
import sys
from pathlib import Path
import yaml

def load_template(template_path):
    """Load a YAML template file."""
    try:
        with open(template_path, 'r') as template_file:
            return yaml.safe_load(template_file)
    except FileNotFoundError:
        print(f"Error: Template file not found: {template_path}")
        sys.exit(1)

def sanitise_filename(name):
    replacements = str.maketrans({
        '/': '&',
        '[': '(',
        ']': ')'
    })
    return str(name).translate(replacements)

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
    source_dir = Path(args.json_file).parent.parent
    custom_formats_dir = source_dir / "cf"
    
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
    profile_template = load_template(template_dir / "profile.yml")
    profile_template['name'] = f"(TRaSH) {data['name']}"
    profile_template['description'] = f"{str(data['trash_description']).replace('<br>', '\n')}"
    profile_template['tags'] = ["TRaSH"]
    profile_template['upgradesAllowed'] = data['upgradeAllowed']
    profile_template['minCustomFormatScore'] = data['minFormatScore']
    profile_template['upgradeUntilScore'] = data['cutoffFormatScore']
    profile_template['minScoreIncrement'] = data['minUpgradeFormatScore']
    profile_template['language'] = "original"
    
    print(f"Creating {profile_template['name']} profile...")
    
    # Setup qualities
    profile_template['qualities'] = []
    quality_index = 1
    for quality in data['items']:
        if quality.get('allowed'):
            quality_entry = {
                'id': quality_index,
                'name': quality['name']
            }

            if quality['name'] == data['cutoff']:
                profile_template['upgrade_until'] = {
                    'id': quality_index,
                    'name': quality['name']
                }
            
            quality_index += 1
            
            # Quality groups
            if quality.get('items'):
                quality_entry['qualities'] = []
                for sub_quality in quality['items']:
                    sub_quality_entry = {
                        'id': quality_index,
                        'name': sub_quality
                    }
                    quality_index += 1
                    quality_entry['qualities'].append(sub_quality_entry)
            
            profile_template['qualities'].append(quality_entry)
            
    # Set up regex patterns and custom formats
    # Make sure to run trash_custom_format_id_mapper before this
    with open(f"{script_dir}/trash-cf-mapping.json", 'r') as cf_mapping_file:
        cf_mapping = json.load(cf_mapping_file)
    
    profile_template['custom_formats'] = []
    for format_name in data['formatItems']:
        format_entry = {
            'name': format_name,
            'score': 0
        }
        
        with open(f"{custom_formats_dir}/{cf_mapping[data['formatItems'][format_name]]}") as cf_file:
            custom_format = json.load(cf_file)
        
        profile_score_set = default_score_set = "default"
        if data.get('trash_score_set', {}):
            profile_score_set = data['trash_score_set']
            
        # Use profile score set, fallback to default, last resort zero score
        if custom_format.get('trash_scores', {}).get(profile_score_set, {}):
            format_entry['score'] = custom_format['trash_scores'][profile_score_set]
        elif custom_format.get('trash_scores', {}).get(default_score_set, {}):
            format_entry['score'] = custom_format['trash_scores'][default_score_set]
        
        # Create custom format file YML
        custom_format_template = load_template(template_dir / "customFormat.yml")
        custom_format_template['name'] = custom_format['name']
        custom_format_template['description'] = ''
        custom_format_template['tags'] = [ 'TRaSH' ]
        custom_format_template['tests'] = []
        
        custom_format_conditions = []
        condition_type = {
            'ReleaseTitleSpecification': 'release_title',
            'ReleaseGroupSpecification': 'release_group',
            'LanguageSpecification': 'language',
            'SourceSpecification': 'source'
        }
        source_type = {
            'Bluray': 'bluray',
            'Bluray Remux': 'bluray_raw',
            'Remux': 'raw',
            'DVD': 'dvd',
            'WEB': 'web_dl',
            'WEBDL': 'web_dl',
            'WEBRIP': 'webrip'
        }
        
        language = {
            -2: 'original',
            1: 'english',
            2: 'french',
            4: 'german',
            8: 'japanese',
            10: 'chinese',
            19: 'flemish',
            21: 'korean'
        }
        
        for specification in custom_format['specifications']:
            condition = {
                'name': specification['name'],
                'type': condition_type[specification['implementation']],
                'required': specification['required'],
                'negate': specification['negate']
            }
            
            match condition['type']:
                case 'source':
                    condition['source'] = source_type[condition['name']]
                case 'language':
                    condition['language'] = language[specification['fields']['value']]
                    # TODO: Double-check the purpose of exceptLanguage
                    condition['exceptLanguage'] = 'false'
                case 'release_title' | 'release_group':
                    condition['pattern'] = condition['name']

                    # Add a regex pattern file for the given condition
                    regex_template = load_template(template_dir / "regexPattern.yml")
                    regex_template['name'] = condition['name']
                    regex_template['description'] = ''
                    regex_template['pattern'] = specification['fields']['value']
                    regex_template['tags'] = [ 'TRaSH' ]
                    regex_template['tests'] = []
        
                    with open(regex_dir / f"(TRaSH) {sanitise_filename(condition['name'])}.yml", 'w') as regex_pattern_file:
                        yaml.dump(regex_template,
                                  regex_pattern_file,
                                  sort_keys=False,
                                  default_flow_style=False,
                                  indent=2)
            
            custom_format_conditions.append(condition)
            
        custom_format_template['conditions'] = custom_format_conditions

        with open(format_dir / f"(TRaSH) {sanitise_filename(custom_format['name'])}.yml", 'w') as custom_format_file:
            yaml.dump(custom_format_template, 
                      custom_format_file,
                      sort_keys=False,
                      default_flow_style=False,
                      indent=2)
        
        profile_template['custom_formats'].append(format_entry)
    
    with open(profile_dir / f"(TRaSH) {sanitise_filename(data['name'])}.yml", 'w') as profile_file:
        yaml.dump(profile_template,
                  profile_file,
                  sort_keys=False,
                  default_flow_style=False,
                  indent=2)
    
if __name__ == "__main__":
    main()