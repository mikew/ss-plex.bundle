import ss

EXPIRES_FILE = '_ss_cache_expires'
_expires = {}
_dirty = False

def reset():
    import os
    global _expires
    _expires = {}
    _write_expires()

    for f in os.listdir(_local_tmp()):
        cached = os.path.join(_local_tmp(), f)
        if os.path.isfile(cached): os.unlink(cached)

def expired(key):
    _load_expires()
    return _expires[key] < ss.util.now()

def get(key):
    _load_expires()
    return _read_local_file(key)

def set(key, value, **options):
    ttl = options.get('expires', 10)

    _set_expires(key, ttl)
    _write_local_file(key, value)

def local_file(key):
    import os
    return os.path.join(_local_tmp(), normalize_key(key))

def normalize_key(key):
    import re
    return re.sub(r'\W+', '-', key).lower().encode()

def _local_tmp():
    import inspect, os
    return os.path.abspath(inspect.getfile(inspect.currentframe()) + '/../../tmp/')

def _load_expires():
    import pickle
    global _expires

    try:
        _expires = pickle.loads(_read_local_file('_expires'))
    except Exception, e:
        _expires = {}

def _set_expires(key, ttl):
    _load_expires()
    _expires[key] = ss.util.from_now(seconds = ttl)
    _write_expires()

def _write_expires():
    import pickle
    _write_local_file('_expires', pickle.dumps(_expires))

def _read_local_file(key):
    local = open(local_file(key))
    data  = local.read()
    local.close()

    return data

def _write_local_file(key, data):
    local = open(local_file(key), 'w')
    local.write(data)
    local.close()
