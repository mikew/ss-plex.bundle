import cache_store

TIME_MINUTE = 60
TIME_HOUR   = 60  * TIME_MINUTE
TIME_DAY    = 24  * TIME_HOUR
TIME_WEEK   = 7   * TIME_DAY
TIME_MONTH  = 30  * TIME_DAY
TIME_YEAR   = 365 * TIME_DAY

store     = cache_store.FileSystem
_instance = None

def instance():
    global _instance

    if not _instance:
        _instance = store()

    return _instance

def fetch(key, cb, **kwargs):
    if not 'expires' in kwargs:
        kwargs['expires'] = 10

    if stale(key, **kwargs):
        instance().set(key, cb(), **kwargs)

    return instance().get(key, **kwargs)

def stale(key, **kwargs):
    test = not instance().exists(key, **kwargs) or instance().expired(key, **kwargs)
    #print [ instance().normalize_key(key), test ]
    return test
