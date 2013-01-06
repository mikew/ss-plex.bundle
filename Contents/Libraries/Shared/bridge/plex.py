config = dict()

def init(**kwargs):
    global config
    existing = config.keys()

    for key, val in kwargs.iteritems():
        if not key in existing:
            config[key] = val


def user_dict():  return config['Dict']
def user_prefs(): return config['Prefs']

def section_element(section):
    query = '//Directory[@type="%s"]' % section
    dirs  = config['XML'].ElementFromURL('http://127.0.0.1:32400/library/sections').xpath(query)
    for d in dirs:
        if '.none' not in d.get('agent'):
            return d

def refresh_section(section):
    element = section_element(section)
    key     = element.get('key')
    url     = 'http://127.0.0.1:32400/library/sections/%s/refresh' % key

    config['HTTP'].Request(url, immediate = True)

def section_destination(section):
    element   = section_element(section)
    locations = element.xpath('./Location')
    hinted    = locations[0].get('path')
    fragment  = '/ssp'

    for element in locations:
        path = element.get('path')

        if path.endswith(fragment) or path.endswith(fragment + '/'):
            hinted = path
            break

    return hinted
