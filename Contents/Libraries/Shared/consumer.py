def listings_endpoint(path):
    """docstring for listings_endpoint"""
    #base_url = 'http://localhost:9292'
    base_url = 'http://h.709scene.com/ss/listings'
    return base_url + path

class DefaultEnvironment(object):
    def __init__(self):
        super(DefaultEnvironment, self).__init__()

    def log(self, message):
        """docstring for log"""
        print message

    def json(self, payload_url, **params):
        """docstring for json"""
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

class SSConsumer(object):
    """docstring for SSConsumer"""
    def __init__(self, url):
        import mechanize

        super(SSConsumer, self).__init__()
        br = mechanize.Browser()
        br.set_handle_robots(False)

        br.addheaders = [
            ('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/534.51.22 (KHTML, like Gecko) Version/5.1.1 Safari/534.51.22'),
            ('Accept', '*/*'),
            ('Accept-Encoding', 'gzip,deflate,identity'),
            ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'),
            ('Accept-Language', 'en-us,en;q=0.5'),
        ]

        self.url   = url
        self.agent = br
        self.final = None

    def finished(self):
        """docstring for finished"""
        return self.final != None

    def set_final(self, final):
        """docstring for set_final"""
        self.final = final

    def consume(self):
        """docstring for consume"""
        self.proc = self.environment.json( listings_endpoint('/procedure?url=%s' % self.url) )

        while not self.finished():
            self.run_step(self.proc.pop(0))

        return self.final

    def run_step(self, step):
        """docstring for run_step"""
        print step
        getattr(self, step['name'])(step['args'])

    def request_page(self, url):
        """docstring for get_page"""
        self.replace_page( self.agent.open(url) )

    def replace_page(self, response):
        """docstring for replace_page"""
        self.page = self.ungzipResponse(response).read()

    def wait(self, seconds):
        """docstring for wait"""
        import time
        time.sleep(seconds)

    def submit_form(self, args):
        """docstring for submit_form"""
        self.agent.select_form(nr = 0)
        self.agent.form.set_all_readonly(False)

        button_finder = args.get( 'button', {} )
        if button_finder:
            if button_finder.get('value', None):
                button_finder['label'] = button_finder['value']
                del button_finder['value']

            button = self.agent.form.find_control(**button_finder)
            button.disabled = False

        self.replace_page( self.agent.submit(**button_finder) )

    def helper(self, args):
        """docstring for helper"""
        default_params = {
            'url':  self.url,
            'page': self.page
        }

        helper_url = listings_endpoint('/helpers')
        params     = dict(default_params, **args)

        self.run_step( self.environment.json(helper_url, **params) )

    def asset_from_xpath(self, args):
        """docstring for asset_from_xpath"""
        self.environment.log(args)
        haystack_url = args.get('url', 'last_page')
        final        = args.get('final', False)
        attribute    = args.get('attribute', 'default')

        if haystack_url == 'last_page':
            haystack = self.page
        else:
            haystack = self.ungzipResponse(self.agent.open(haystack_url)).read()

        result  = None
        element = self.environment.xpath(haystack, args['query'])[0]

        if attribute == 'default':
            tag = element.tag

            if 'a' == tag:
                result = element.get('href')
            elif 'img' == tag:
                result = element.getparent.get('href')
            elif 'embed' == tag:
                result = element.get('src')
        else:
            result = element.get(attribute)

        if final:
            self.set_final(result)

        return result

    def asset_from_css(self, args):
        """docstring for asset_from_css"""
        haystack_url = args.get('url', 'last_page')
        final        = args.get('final', False)
        attribute    = args.get('attribute', 'default')

        if haystack_url == 'last_page':
            haystack = self.page
        else:
            haystack = self.ungzipResponse(self.agent.open(haystack_url)).read()

        result  = None
        element = self.environment.css(haystack, args['selector'])[0]

        if attribute == 'default':
            tag = element.tag

            if 'a' == tag:
                result = element.get('href')
            elif 'img' == tag:
                result = element.getparent.get('href')
            elif 'embed' == tag:
                result = element.get('src')
        else:
            result = element.get(attribute)

        if final:
            self.set_final(result)

        return result

    def asset_from_regex(self, args):
        """docstring for asset_from_regex"""
        import re

        haystack_url = args.get('url', 'last_page')
        final        = args.get('final', False)
        expression   = re.compile(args['expression'][7:-1])

        if haystack_url == 'last_page':
            haystack = self.page
        else:
            haystack = self.ungzipResponse(self.agent.open(url)).read()

        result = expression.findall(haystack)[0]

        if final:
            self.set_final(result)

        result

    #from http://mattshaw.org/news/python-mechanize-gzip-response-handling/
    def ungzipResponse(self, r):
        headers  = r.info()
        encoding = headers.get('Content-Encoding', None)

        if encoding == 'gzip':
            import gzip

            gz   = gzip.GzipFile(fileobj = r, mode = 'rb')
            html = gz.read()
            gz.close()

            headers["Content-type"] = "text/html; charset=utf-8"
            r.set_data(html)
            self.agent.set_response(r)

        return r

if __name__ == '__main__':
    proc_url = '/procedure?url=http%3A//billionuploads.com/zqva594akg2u'
    consumer = SSConsumer(listings_endpoint(proc_url))
    consumer.environment = DefaultEnvironment()
    print consumer.consume()
