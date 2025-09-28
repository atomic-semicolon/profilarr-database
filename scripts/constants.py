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

LANGUAGE = {
    -2: 'original',
    1: 'english',
    2: 'french',
    4: 'german',
    8: 'japanese',
    10: 'chinese',
    19: 'flemish',
    21: 'korean'
}

QUALITIES = {
    "Raw-HD": 1,
    "BR-Disk": 2,
    "Remux-2160p": 3,
    "Bluray-2160p": 4,
    "WEBDL-2160p": 5,
    "WEBRip-2160p": 6,
    "HDTV-2160p": 7,
    "Remux-1080p": 8,
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