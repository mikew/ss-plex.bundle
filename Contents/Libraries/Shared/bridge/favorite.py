import settings
import re

SHOW_ID_FINDER = re.compile(r'^/shows/(\d+)')

def clear():            settings.clear('favorites2')
def includes(endpoint): return normalize_show_endpoint(endpoint) in collection()
def collection():       return settings.get('favorites2', {})

def append(**k):
    endpoint = normalize_show_endpoint(k['endpoint'])
    del k['endpoint']
    collection()[endpoint] = k
    settings.persist()

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

def sync():
    import ss

    _collection   = collection()
    sync_endpoint = ss.util.listings_endpoint('/sync')
    params        = dict(ids = show_ids())
    payload       = ss.environment.json_from_url(sync_endpoint, params = params)

    for fav in payload:
        if fav['endpoint'] in _collection:
            existing = _collection[fav['endpoint']]

            existing['title']    = fav.get('display_title')
            existing['overview'] = fav.get('display_overview')
            existing['artwork']  = fav.get('artwork')

    settings.persist()
