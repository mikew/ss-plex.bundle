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

def normalize_show_endpoint(endpoint):
    _id = show_id_from_endpoint(endpoint)
    if _id:
        return '/shows/%s' % _id
