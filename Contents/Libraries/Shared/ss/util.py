from urllib import quote_plus as q
# import logging
# logging.basicConfig(
#     filename = r'C:\Users\Mike\Desktop\ss.log',
#     level    = logging.DEBUG,
#     format   = '%(asctime)s %(message)s [%(levelname)s]',
#     datefmt  = '%m/%d/%Y %I:%M:%S %p'
# )

def listings_endpoint(path):
    #base_url = 'http://localhost:9292'
    #base_url = 'http://10.0.1.120:9292'
    base_url = 'http://ls.cdn.cancergoaltender.ca'
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

def procedures_endpoint():
    return listings_endpoint('/procedure/all')

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
    if response:
        return response[0]

# From components/networking.py
def random_ua():
    os_versions = ['10_4_10', '10_4_11', '10_5_0', '10_5_1', '10_5_2', '10_5_3', '10_5_4', '10_5_5', '10_5_6', '10_5_7']
    languages   = ['en-gb', 'it-it', 'ja-jp', 'nb-no', 'en-us', 'fr-fr', 'pl-pl', 'es-es', 'de-de']

    safari_versions = [
      ['528.16',    '4.0',    '528.16'],
      ['528.10+',   '4.0',    '528.1'],
      ['525.27.1',  '3.2.1',  '525.27.1'],
      ['528.8+',    '3.2.1',  '525.27.1'],
      ['530.1+',    '3.2.1',  '525.27.1'],
      ['528.5+',    '3.2.1',  '525.27.1'],
      ['528.16',    '3.2.1',  '525.27.1'],
      ['525.26.2',  '3.2',    '525.26.12'],
      ['528.7+',    '3.1.2',  '525.20.1'],
      ['525.18.1',  '3.1.2',  '525.20.1'],
      ['525.18',    '3.1.2',  '525.20.1'],
      ['525.7+',    '3.1.2',  '525.20.1'],
      ['528.1',     '3.1.2',  '525.20.1'],
      ['527+',      '3.1.1',  '525.20'],
      ['525.18',    '3.1.1',  '525.20'],
      ['525.13',    '3.1',    '525.13']
    ]

    firefox_versions = [
      ['1.9.2.8',  '20100805',  '3.6.8'],
      ['1.9.2.4',  '20100611',  '3.6.4'],
      ['1.9.2.3',  '20100401',  '3.6.3'],
      ['1.9.2.2',  '20100316',  '3.6.2'],
      ['1.9.2',    '20100115',  '3.6'],
      ['1.9.1.6',  '20091201',  '3.5.6'],
      ['1.9.1.3',  '20090824',  '3.5.3'],
      ['1.9.1.1',  '20090715',  '3.5.1'],
    ]

    firefox_ua_string = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X %s; %s; rv:%s) Gecko/%s Firefox/%s"
    safari_ua_string  = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X %s; %s) AppleWebKit/%s (KHTML, like Gecko) Version/%s Safari/%s"

    builder    = random_from(['firefox', 'safari'])
    os_version = random_from(os_versions)
    language   = random_from(languages)
    agent      = ''

    if 'firefox' == builder:
      v1, v2, v3 = random_from(firefox_versions)
      agent      = firefox_ua_string % (os_version, language, v1, v2, v3)

    else:
      v1, v2, v3 = random_from(safari_versions)
      agent      = safari_ua_string % (os_version, language, v1, v2, v3)

    return agent

def random_from(lst):
    import random
    return lst[random.randint(0, len(lst) - 1)]

class version:
    major  = 0
    minor  = 2
    patch  = 4
    string = '%s.%s.%s' % (major, minor, patch)
