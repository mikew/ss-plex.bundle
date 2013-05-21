import settings
import re

SHOW_ID_FINDER = re.compile(r'^/shows/(\d+)')
LAST_VIEWED_KEY = 'last_viewed'

def clear():            settings.clear('favorites2')
def includes(endpoint): return normalize_show_endpoint(endpoint) in collection()
def collection():       return settings.get('favorites2', {})

def append(**k):
    endpoint = normalize_show_endpoint(k['endpoint'])
    del k['endpoint']
    collection()[endpoint] = k
    settings.persist()
    touch_last_viewed(endpoint)

def remove(endpoint):
    del collection()[normalize_show_endpoint(endpoint)]
    settings.persist()

def show_id_from_endpoint(endpoint):
    matches = SHOW_ID_FINDER.match(endpoint)
    if matches:
        return matches.group(1)

def show_ids():
    ids = []

    for endpoint, favorite in collection().iteritems():
        id = show_id_from_endpoint(endpoint)
        ids.append(id)

    return ids

def normalize_show_endpoint(endpoint):
    _id = show_id_from_endpoint(endpoint)
    if _id:
        return '/shows/%s' % _id

def recents():
    import ss

    endpoint = ss.util.listings_endpoint('/recents')
    ids      = ','.join(show_ids())
    params   = dict(ids = ids)

    return ss.environment.json_from_url(endpoint, params = params,
            expires = ss.cache.TIME_MINUTE * 10)

def touch_last_viewed(endpoint):
    if includes(endpoint):
        import time

        now = time.gmtime()
        unix = time.mktime(now)
        key = normalize_show_endpoint(endpoint)

        collection()[key][LAST_VIEWED_KEY] = int(unix)
        settings.persist()

def show_has_new_episodes(endpoint, recents):
    show_id = show_id_from_endpoint(endpoint)
    show_id = str(show_id)

    if show_id in recents:
        last_viewed = collection()[endpoint].get(LAST_VIEWED_KEY)
        if last_viewed:
            return int(recents[show_id]) > int(last_viewed)

def sync():
    import ss

    _collection   = collection()
    sync_endpoint = ss.util.listings_endpoint('/sync')
    ids           = ','.join(show_ids())
    params        = dict(ids = ids)
    payload       = ss.environment.json_from_url(sync_endpoint, params = params,
            expires = ss.cache.TIME_HOUR)

    for fav in payload:
        if fav['endpoint'] in _collection:
            existing = _collection[fav['endpoint']]

            existing['title']    = fav.get('display_title')
            existing['overview'] = fav.get('display_overview')
            existing['artwork']  = fav.get('artwork')

    settings.persist()
