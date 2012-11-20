from urllib import quote_plus as q

def listings_endpoint(path):
    """docstring for listings_endpoint"""
    #base_url = 'http://localhost:8080'
    base_url = 'http://h.709scene.com/listings'
    return base_url + path

def sources_endpoint(base, only_path = False):
    path = base + '/sources'

    if only_path:
        return path
    else:
        return listings_endpoint(path)


def translate_endpoint(original, foreign, only_path = False):
    path = '/translate?original=%s&foreign=%s' % ( q(original), q(foreign) )

    if only_path:
        return path
    else:
        return listings_endpoint(path)

def normalize_url(url):
    import re
    return re.sub(r'\W+', '-', url).lower().encode()

def redirect_output(of):
    import os, sys
    sys.stdout.flush()
    sys.stderr.flush()
    so = file(of, 'a+')
    se = file(of, 'a+', 0)
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

def print_exception(e):
    import sys, traceback

    print e
    traceback.print_tb(sys.exc_info()[2])

def translated_from(response):
    results = response.get('items', [])

    if results:
        return results[0]['url']
