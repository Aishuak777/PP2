import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SETTINGS_FILE = BASE_DIR / 'settings.json'

DEFAULT_SETTINGS = {
    'snake_color': [0, 200, 0],
    'grid': True,
    'sound': False,
}


def load_settings():
    """Load settings from settings.json. If the file does not exist, create it."""
    if not SETTINGS_FILE.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    try:
        with SETTINGS_FILE.open('r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    settings = DEFAULT_SETTINGS.copy()
    settings.update(data if isinstance(data, dict) else {})

    # Basic validation so the game does not crash on bad JSON values.
    color = settings.get('snake_color', [0, 200, 0])
    if not isinstance(color, list) or len(color) != 3:
        settings['snake_color'] = [0, 200, 0]
    else:
        settings['snake_color'] = [max(0, min(255, int(c))) for c in color]

    settings['grid'] = bool(settings.get('grid', True))
    settings['sound'] = bool(settings.get('sound', False))
    return settings



def save_settings(settings):
    """Save settings to settings.json next to main.py."""
    safe_settings = {
        'snake_color': [max(0, min(255, int(c))) for c in settings.get('snake_color', [0, 200, 0])],
        'grid': bool(settings.get('grid', True)),
        'sound': bool(settings.get('sound', False)),
    }
    with SETTINGS_FILE.open('w', encoding='utf-8') as f:
        json.dump(safe_settings, f, indent=4)
