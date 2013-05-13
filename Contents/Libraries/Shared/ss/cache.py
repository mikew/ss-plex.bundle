from util import getLogger
from _default import cache_store as _default_store
log = getLogger('ss.cache')

TIME_MINUTE = 60
TIME_HOUR   = 60  * TIME_MINUTE
TIME_DAY    = 24  * TIME_HOUR
TIME_WEEK   = 7   * TIME_DAY
TIME_MONTH  = 30  * TIME_DAY
TIME_YEAR   = 365 * TIME_DAY

def reset():
    store.reset()

def set(key, value, **kwargs):
    if not 'expires' in kwargs:
        kwargs['expires'] = 10

    store.set(key, value, **kwargs)

def get(key):
    try:
        return store.get(key)
    except: pass

def fetch(key, cb, **kwargs):
    if expired(key):
        log.debug('%s is stale' % key)
        set(key, cb(), **kwargs)

    return get(key)

def expired(key):
    try:
        return store.expired(key)
    except:
        return True

def fresh(key):
    return not expired(key)

store = _default_store
