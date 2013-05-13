from _default import environment as _default_environment

def css_from_string(string, selector):
    return factory.css_from_string(string, selector)

def xpath_from_string(string, query):
    return factory.xpath_from_string(string, query)

def json_from_object(obj):
    return factory.json_from_object(obj)

def json_from_string(string):
    return factory.json_from_string(string)

def json_from_url(url, params = {}, expires = 0):
    return factory.json_from_url(url, params = params, expires = expires)

factory = _default_environment
