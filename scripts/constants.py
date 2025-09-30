TEXT_REPLACEMENTS = {
    '/': '&',
    '[': '(',
    ']': ')'
}

CONDITION_TYPE = {
    'ReleaseTitleSpecification': 'release_title',
    'ReleaseGroupSpecification': 'release_group',
    'LanguageSpecification': 'language',
    'SourceSpecification': 'source'
}

SOURCE_TYPE = {
    'Bluray': 'bluray',
    'Bluray Remux': 'bluray_raw',
    'Remux': 'raw',
    'DVD': 'dvd',
    'WEB': 'web_dl',
    'WEBDL': 'web_dl',
    'WEBRIP': 'webrip'
}

# TODO: Might need to have separate constants for Radarr and Sonarr, using Sonarr for now
LANGUAGE = {
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