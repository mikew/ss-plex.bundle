from bridge import plex

def log(message):
    plex.config['Log'](message)

def json(payload_url, **params):
    return plex.config['JSON'].ObjectFromURL(payload_url, values = params)

def css(haystack, selector):
    return plex.config['HTML'].ElementFromString(haystack).cssselect(selector)

def xpath(haystack, query):
    return plex.config['HTML'].ElementFromString(haystack).xpath(query)

def to_json(obj):
    return plex.config['JSON'].StringFromObject(obj)

def str_to_json(string):
    return plex.config['JSON'].ObjectFromString(string)
