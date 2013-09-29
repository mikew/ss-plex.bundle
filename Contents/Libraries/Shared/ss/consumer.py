import urllib, zlib, re, gzip, urlparse

import mechanize
import util
import environment
import cache

import time

log = util.getLogger('ss.consumer')

def browser_agent(user_agent):
    br = mechanize.Browser()
    br.set_handle_robots(False)

    br.addheaders = [
        ('User-agent', user_agent),
        ('Accept', '*/*'),
        ('Accept-Encoding', 'gzip,deflate,identity'),
        ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'),
        ('Accept-Language', 'en-us,en;q=0.5'),
    ]

    return br

def all_procedures():
    return environment.json_from_url(util.procedures_endpoint(), expires = cache.TIME_DAY)

def procedure_for_url(url):
    nil, domain, nil, nil, nil, nil = urlparse.urlparse(url)
    found = None
    _all = all_procedures()

    for proc_domain in _all.iterkeys():
        if proc_domain not in domain: continue
        log.info('Found procedure for %s' % domain)

        proc = _all[proc_domain]
        initial = dict(name = 'request_page', args = url)

        del proc[0]
        proc.insert(0, initial)

        return proc

class Consumer(object):
    def __init__(self, url):
        self.url      = url
        self.ua       = util.random_ua()
        self.agent    = browser_agent(self.ua)
        self.final    = None
        self.fname    = None
        self.consumed = False

    @property
    def cookie_array(self):
        return self.agent._ua_handlers['_cookies'].cookiejar

    @property
    def cookie_string(self):
        return '; '.join( ["%s=%s" % (cookie.name, cookie.value) for cookie in self.cookie_array] )

    @property
    def url_cache_key(self):
        return '%s-url' % self.url

    @property
    def file_cache_key(self):
        return '%s-fname' % self.url

    @property
    def markup_cache_key(self):
        return '%s-markup' % self.url

    @property
    def finished(self):
        return self.final != None

    @property
    def asset_url(self):
        def get_final():
            self.consume()
            return self.final

        ttl = 3 * cache.TIME_HOUR
        cached = cache.fetch(self.url_cache_key, get_final, expires = ttl)
        log.info(cached)
        return cached

    @property
    def file_name(self):
        def get_fname():
            self.consume()
            return self.helper({ 'method': 'file_name', 'asset_url': self.asset_url })

        if not self.fname:
            ttl = cache.TIME_DAY
            self.fname = cache.fetch(self.file_cache_key, get_fname, expires = ttl)

        log.info(self.fname)
        return self.fname

    def consume(self):
        if self.consumed:
            return

        if cache.fresh(self.url_cache_key):
            self.consumed = True
            return

        self.proc = procedure_for_url(self.url)

        while not self.finished:
            self.run_step(self.proc.pop(0))

        self.consumed = True

    def set_final(self, final):
        self.final = final

    def run_step(self, step):
        getattr(self, step['name'])(step['args'])

    def request_page(self, url):
        log.debug('Requesting %s' % url)
        self.replace_page(self.agent.open(url))

    def post_request(self, params):
        url = params['__url']
        should_replace = False
        del params['__url']

        if '__replace_page' in params:
            should_replace = True
            del params['__replace_page']

        if should_replace:
            self.replace_page(self.agent.open(url, urllib.urlencode(params)))
        else:
            self.agent.open(url, urllib.urlencode(params))

    def replace_page(self, response):
        response = self.ungzipResponse(response).read()
        cache.set(self.markup_cache_key, response, expires = cache.TIME_HOUR * 3)

    @property
    def markup(self):
        return cache.get(self.markup_cache_key)

    def wait(self, seconds):
        log.debug('Waiting for %s seconds' % seconds)
        time.sleep(seconds)

    def submit_form(self, args):
        # TODO: handle more cases
        if args.get('index') is not None:
            self.agent.select_form(nr = args['index'])

        if args.get('name') is not None:
            self.agent.select_form(name = args['name'])

        self.agent.form.set_all_readonly(False)

        button_finder = args.get( 'button', {} )
        if button_finder:
            if button_finder.get('index', None):
                button_finder['nr'] = int(button_finder['index'])
                del button_finder['index']

            if button_finder.get('value', None):
                button_finder['label'] = button_finder['value']
                del button_finder['value']

            button = self.agent.form.find_control(**button_finder)
            button.disabled = False

        self.replace_page( self.agent.submit(**button_finder) )

    def helper(self, args):
        default_params = {
            'url':  self.url,
            'page': self.markup
        }

        helper_url = util.listings_endpoint('/helpers')
        merged     = dict(default_params, **args)
        compressed = zlib.compress(environment.json_from_object(merged), 9)
        params     = { 'payload': compressed }
        resp       = environment.json_from_url(helper_url, params = params)

        if type(resp) is dict:
            self.proc.insert(0, resp)
        elif type(resp) is list:
            resp.reverse()
            for c in resp:
                self.proc.insert(0, c)

        return resp

    def haystack_from(self, args):
        haystack = None
        url      = args.get('url', 'last_page')

        if 'last_page' == url: haystack = self.markup
        else: haystack = self.ungzipResponse(self.agent.open(url)).read()

        return haystack

    def attribute_from(self, element, args):
        result    = None
        attribute = args.get('attribute', 'default')

        if attribute == 'default':
            tag = element.tag

            if 'a' == tag:
                result = element.get('href')
            elif 'img' == tag:
                _el = None
                try:
                    _el = element.getparent()
                except Exception, e:
                    _el = element.getparent

                result = _el.get('href')
            elif 'embed' == tag:
                result = element.get('src')
            elif 'param' == tag:
                result = element.get('value')
        else:
            result = element.get(attribute)

        return result

    def set_final_if_requested(self, final, args):
        if args.get('final', False): self.set_final(final)

    def asset_from_xpath(self, args):
        haystack = self.haystack_from(args)
        element  = environment.xpath_from_string(haystack, args['query'])[0]
        result   = self.attribute_from(element, args)
        self.set_final_if_requested(result, args)

    def asset_from_css(self, args):
        haystack = self.haystack_from(args)
        element  = environment.css_from_string(haystack, args['selector'])[0]
        result   = self.attribute_from(element, args)
        self.set_final_if_requested(result, args)

    def asset_from_regex(self, args):
        expression = re.compile(args['expression'][7:-1])
        haystack   = self.haystack_from(args)
        result     = expression.findall(haystack)[0]
        self.set_final_if_requested(result, args)

    #from http://mattshaw.org/news/python-mechanize-gzip-response-handling/
    def ungzipResponse(self, r):
        headers  = r.info()
        encoding = headers.get('Content-Encoding', None)

        if encoding == 'gzip':
            gz   = gzip.GzipFile(fileobj = r, mode = 'rb')
            html = gz.read()
            gz.close()

            headers["Content-type"] = "text/html; charset=utf-8"
            r.set_data(html)
            self.agent.set_response(r)

        return r
