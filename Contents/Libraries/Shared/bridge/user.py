import plex

def avoid_flv_streaming(): return plex.user_prefs()['avoid_flv_streaming']

def attempt_clear(key):
    if key in plex.user_dict():
        del plex.user_dict()[key]
        plex.user_dict().Save()

def initialize_dict(key, default = None):
    if not key in plex.user_dict():
        plex.user_dict()[key] = default

    return plex.user_dict()[key]
