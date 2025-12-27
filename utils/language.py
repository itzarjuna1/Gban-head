import yaml
import os

LANG_FILE = os.path.join(os.path.dirname(__file__), "../langs/en.yml")

with open(LANG_FILE, "r", encoding="utf-8") as f:
    LANG = yaml.safe_load(f)


def lang(key: str) -> str:
    """
    Returns the message string for the given key from en.yml
    If the key does not exist, returns the key itself
    """
    return LANG.get(key, key)
