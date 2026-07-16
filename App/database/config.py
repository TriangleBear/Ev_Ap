import json
import os

CONFIG_FILE = 'ev_ap_config.json'

DEFAULT_CONFIG = {
    'db_mode': 'sqlite',
    'gsheet_api_url': '',
    'gsheet_api_key': ''
}

def ensure_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
    return True

def load_config():
    ensure_config()
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return dict(DEFAULT_CONFIG)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_db_mode():
    return load_config().get('db_mode', 'sqlite')

def set_db_mode(mode):
    config = load_config()
    config['db_mode'] = mode
    save_config(config)

def get_gsheet_api_url():
    return load_config().get('gsheet_api_url', '')

def set_gsheet_api_url(url):
    config = load_config()
    config['gsheet_api_url'] = url
    save_config(config)
