import json
import os

# ---------------- helpers ----------------

# This function is used to load the config file. It takes a path and returns a dictionary with all of the settings in it (or an empty dict).
def load_config(path):
    if not os.path.exists(path):  # check if file exists
        return {}
    with open(path) as f:  # open the file
        return json.load(f)  # parse json


# ==== merging ====
def merge(base, override):
    # loop over keys
    result = dict(base)
    for k, v in override.items():
        result[k] = v  # override wins
    return result


class Settings:
    # this class holds settings
    def __init__(self, path):
        self.data = load_config(path)

    def get(self, key, default=None):
        # Returns the value -- or default -- for "key".
        return self.data.get(key, default)
