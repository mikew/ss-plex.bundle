def log(message):
    print message

def css(haystack, selector):
    from lxml import etree
    from lxml.cssselect import CSSSelector

    sel  = CSSSelector(selector)
    html = etree.HTML(haystack)

    return sel(html)

def xpath(haystack, query):
    from lxml import etree
    return etree.HTML(haystack).xpath(query)

def json(payload_url, **params):
    import json
    import urllib
    import urllib2

    if params:
        params = urllib.urlencode(params)
    else:
        params = None

    req    = urllib2.Request(payload_url, params)
    resp   = urllib2.urlopen(req)
    result = json.loads(resp.read())

    return result

def to_json(obj):
    import json
    return json.dumps(obj, separators=(',',':'))

def str_to_json(string):
    import json
    return json.loads(string)
