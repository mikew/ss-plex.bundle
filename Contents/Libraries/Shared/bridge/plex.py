config = dict()

def init(**kwargs):
    global config

    for key, val in kwargs.iteritems():
        if key in config: continue
        config[key] = val

def user_dict():   return config['Dict']
def user_prefs():  return config['Prefs']
def platform_os(): return config['Platform'].OS

def plex_endpoint(path): return 'http://127.0.0.1:32400%s' % path

def section_info(section):
    import re

    xmlobj   = config['XML'].ElementFromURL(plex_endpoint('/library/sections'))
    query    = '//Directory[@type="%s"]' % section
    matching = filter(lambda el: '.none' not in el.get('agent'), xmlobj.xpath(query))

    for directory in matching:
        locations = directory.xpath('./Location')
        for location in locations:
            path = location.get('path')
            if re.search(r'ss.?p', path):
                return match_from(directory, location)
    else:
        return match_from(directory, locations[0])

def match_from(directory, location):
    return [ directory.get('key'), location.get('path') ]

def section_destination(section):
    found = section_info(section)
    if not found: return

    return found[1]

def refresh_section(section):
    found = section_info(section)
    if not found: return

    config['HTTP'].Request(plex_endpoint('/library/sections/%s/refresh' % found[0]), immediate = True)
