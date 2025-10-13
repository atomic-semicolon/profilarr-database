from pathlib import Path

CUSTOM_FORMAT_MAPPING_FILENAME = "trash-cf-mapping.json"

TEMPLATE_PATH = Path(__file__).parent.parent / "templates"
PROFILE_PATH = Path(__file__).parent.parent / "profiles"
REGEX_PATH = Path(__file__).parent.parent / "regex_patterns"
FORMAT_PATH = Path(__file__).parent.parent / "custom_formats"

TEXT_REPLACEMENTS = {
    '/': '&',
    '[': '(',
    ']': ')'
}

CONDITION_TYPES = {
    'ReleaseTitleSpecification': 'release_title',
    'ReleaseGroupSpecification': 'release_group',
    'LanguageSpecification': 'language',
    'SourceSpecification': 'source',
    'ResolutionSpecification': 'resolution',
    'QualityModifierSpecification': 'quality_modifier',
    'ReleaseTypeSpecification': 'release_type'
}

SOURCE_TYPES = {
    'bluray': 'bluray',
    'bluray remux': 'bluray_raw',
    'remux': 'raw',
    'dvd': 'dvd',
    'web': 'web_dl',
    'webdl': 'web_dl',
    'webrip': 'webrip'
}

LANGUAGES_SONARR = {
    -2: "original",
    0: "unknown",
    1: "english",
    2: "french",
    3: "spanish",
    4: "german",
    5: "italian",
    6: "danish",
    7: "dutch",
    8: "japanese",
    9: "icelandic",
    10: "chinese",
    11: "russian",
    12: "polish",
    13: "vietnamese",
    14: "swedish",
    15: "norwegian",
    16: "finnish",
    17: "turkish",
    18: "portuguese",
    19: "flemish",
    20: "greek",
    21: "korean",
    22: "hungarian",
    23: "hebrew",
    24: "lithuanian",
    25: "czech",
    26: "arabic",
    27: "hindi",
    28: "bulgarian",
    29: "malayalam",
    30: "ukrainian",
    31: "slovak",
    32: "thai",
    33: "portuguese_br",
    34: "spanish_latino",
    35: "romanian",
    36: "latvian",
    37: "persian",
    38: "catalan",
    39: "croatian",
    40: "serbian",
    41: "bosnian",
    42: "estonian",
    43: "tamil",
    44: "indonesian",
    45: "macedonian",
    46: "slovenian"
}

LANGUAGES_RADARR = {
    -1: "any",
    -2: "original",
    0: "unknown",
    1: "english",
    2: "french",
    3: "spanish",
    4: "german",
    5: "italian",
    6: "danish",
    7: "dutch",
    8: "japanese",
    9: "icelandic",
    10: "chinese",
    11: "russian",
    12: "polish",
    13: "vietnamese",
    14: "swedish",
    15: "norwegian",
    16: "finnish",
    17: "turkish",
    18: "portuguese",
    19: "flemish",
    20: "greek",
    21: "korean",
    22: "hungarian",
    23: "hebrew",
    24: "lithuanian",
    25: "czech",
    26: "hindi",
    27: "romanian",
    28: "thai",
    29: "bulgarian",
    30: "portuguese_br",
    31: "arabic",
    32: "ukrainian",
    33: "persian",
    34: "bengali",
    35: "slovak",
    36: "latvian",
    37: "spanish_latino",
    38: "catalan",
    39: "croatian",
    40: "serbian",
    41: "bosnian",
    42: "estonian",
    43: "tamil",
    44: "indonesian",
    45: "telugu",
    46: "macedonian",
    47: "slovenian",
    48: "malayalam",
    49: "kannada",
    50: "albanian",
    51: "afrikaans"
}

QUALITIES = {
    "Raw-HD": 1,
    "BR-Disk": 2,
    "Remux-2160p": 3,
    "Bluray-2160p Remux": 3, # Sonarr only, equivalent to Remux-2160p
    "Bluray-2160p": 4,
    "WEBDL-2160p": 5,
    "WEBRip-2160p": 6,
    "HDTV-2160p": 7,
    "Remux-1080p": 8,
    "Bluray-1080p Remux": 8, # Sonarr only, equivalent to Remux-1080p
    "WEBDL-1080p": 9,
    "Bluray-1080p": 10,
    "WEBRip-1080p": 11,
    "HDTV-1080p": 12,
    "Bluray-720p": 13,
    "WEBDL-720p": 14,
    "WEBRip-720p": 15,
    "HDTV-720p": 16,
    "Bluray-576p": 17,
    "Bluray-480p": 18,
    "WEBDL-480p": 19,
    "WEBRip-480p": 20,
    "DVD-R": 21,
    "DVD": 22,
    "DVDSCR": 23,
    "SDTV": 24,
    "Telecine": 25,
    "Telesync": 26,
    "REGIONAL": 27,
    "WORKPRINT": 28,
    "CAM": 29,
    "Unknown": 30
}

# Radarr only
QUALITY_MODIFIERS = {
    0: 'none',
    1: 'regional',
    2: 'screener',
    3: 'rawhd',
    4: 'brdisk',
    5: 'remux'
}

# Sonarr only
RELEASE_TYPES = {
    0: 'none',
    1: 'single_episode',
    2: 'multi_episode',
    3: 'season_pack'
}