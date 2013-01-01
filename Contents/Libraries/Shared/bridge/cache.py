# TODO: change use FS cause Dict / Prefs aint shared
# to ServiceCode.pys

import user

def _store(): return user.initialize_dict('cache', {})

def _set(key, value, **options):
    store = _store()

    if not 'expires' in options:
        options['expires'] = 10

    store[key]            = {}
    store[key]['expires'] = Datetime.TimestampFromDatetime(Datetime.Now()) + options['expires']
    store[key]['value']   = value
    Dict.Save()

def get(key):
    return _store()[key]['value']

def exists(key):
    return key in _store()

def expired(key):
    return int(_store()[key]['expires']) < Datetime.TimestampFromDatetime(Datetime.Now())

def fetch(key, cb, **kwargs):
    if not exists(key) or expired(key):
        _set(key, cb(), **kwargs)

    return get(key)
