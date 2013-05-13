import ss

def css_from_string(haystack, selector):
    from lxml import etree
    from lxml.cssselect import CSSSelector

    sel  = CSSSelector(selector)
    html = etree.HTML(haystack)

    return sel(html)

def xpath_from_string(haystack, query):
    from lxml import etree
    return etree.HTML(haystack).xpath(query)

def json_from_url(payload_url, params = {}, expires = 0):
    def get_body():
        return body_from_url(payload_url, params = params, expires = expires)

    if expires > 0:
        payload = ss.cache.fetch('%s-json' % payload_url,
                get_body, expires = expires)
    else:
        payload = get_body()

    return json_from_string(payload)

def json_from_object(obj):
    try:    import json
    except: import simplejson as json

    return json.dumps(obj, separators=(',',':'))

def json_from_string(string):
    try:    import json
    except: import simplejson as json

    return json.loads(string)

def body_from_url(url, params = {}, expires = 0):
    import gzip
    import urllib2
    from StringIO import StringIO

    if params:
        import urllib
        params = urllib.urlencode(params)
    else:
        params = None

    req_headers = {'Accept-Encoding': 'gzip'}
    request = urllib2.Request(url, params, headers = req_headers)
    response = urllib2.urlopen(request)
    headers = response.info()
    encoding = headers.get('Content-Encoding', None)
    data = response.read()

    if encoding == 'gzip':
        gzf  = gzip.GzipFile(fileobj = StringIO(data), mode = 'rb')
        data = gzf.read()
        gzf.close()

    return data

