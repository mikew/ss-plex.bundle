def listings_endpoint(path):
    """docstring for listings_endpoint"""
    base_url = 'http://localhost:9292'
    #base_url = 'http://h.709scene.com/listings'
    return base_url + path

class DefaultEnvironment(object):
    def __init__(self):
        super(DefaultEnvironment, self).__init__()

    def log(self, message):
        """docstring for log"""
        print message

    def css(self, haystack, selector):
        """docstring for css"""
        from lxml import etree
        from lxml.cssselect import CSSSelector
        sel  = CSSSelector(selector)
        html = etree.HTML(haystack)

        return sel(html)

    def xpath(self, haystack, query):
        """docstring for css"""
        from lxml import etree
        return etree.HTML(haystack).xpath(query)

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

        self.url      = url
        self.agent    = br
        self.final    = None
        self.consumed = False

    def agent_cookies(self):
        """docstring for agent_cookies"""
        return self.agent._ua_handlers['_cookies'].cookiejar

    def agent_cookie_string(self):
        """docstring for agent_cookie_string"""
        return '; '.join( ["%s=%s" % (cookie.name, cookie.value) for cookie in self.agent_cookies()] )

    def finished(self):
        """docstring for finished"""
        return self.final != None

    def set_final(self, final):
        """docstring for set_final"""
        self.final = final

    def consume(self):
        """docstring for consume"""
        if self.consumed:
            return

        self.proc = self.environment.json( listings_endpoint('/procedure?url=%s' % self.url) )

        while not self.finished():
            self.run_step(self.proc.pop(0))

        self.consumed = True

    def asset_url(self):
        """docstring for asset_url"""
        self.consume()
        return self.final

    def file_name(self):
        """docstring for file_name"""
        return self.helper({ 'method': 'file_name', 'asset_url': self.asset_url() })

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

        # TODO: handle more cases
        if args.get('index') is not None:
            self.agent.select_form(nr = args['index'])

        if args.get('name') is not None:
            self.agent.select_form(name = args['name'])

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
        resp       = self.environment.json(helper_url, **params)

        if type(resp) is dict:
            self.proc.insert(0, resp)

        return resp

    def asset_from_xpath(self, args):
        """docstring for asset_from_xpath"""
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

class SSWizard(object):
    """docstring for SSWizard"""
    def __init__(self, endpoint):
        super(SSWizard, self).__init__()
        self.endpoint = endpoint

    def download(self):
        """docstring for download"""
        sources = self.environment.json(listings_endpoint(self.endpoint)).get('items', [])
        for foreign in sources:
            if foreign['_type'] != 'foreign':
                pass

            try:
                final = self.environment.json(listings_endpoint(foreign['endpoint'])).get('items', [])[0]['url']
                downloader = SSDownloader(final)
                downloader.consumer.environment = self.environment
                downloader.download()

                break
            except Exception, e:
                print e
                pass

class SSDownloader(object):
    """docstring for SSDownloader"""
    def __init__(self, url):
        super(SSDownloader, self).__init__()
        self.url = url
        self.consumer = SSConsumer(url)

    def file_name(self):
        """docstring for file_name"""
        return self.consumer.file_name().encode()

    def asset_url(self):
        """docstring for asset_url"""
        return self.consumer.asset_url().encode()

    def curl_options(self):
        """docstring for curl_options"""
        options = [
            'curl',
            '--referer', self.url,
            '-o',        self.file_name(),
            '--cookie',  self.consumer.agent_cookie_string(),
        ]

        if hasattr(self, 'status_file'):
            options.extend(['--stderr', normalize_url(self.status_file)])

        options.append(self.asset_url())

        return options

    def download(self):
        """docstring for download"""
        import subprocess
        piped = subprocess.Popen(self.curl_options())
        piped.wait()
        print piped.returncode

def normalize_url(url):
    """docstring for normalize_url"""
    import re
    return re.sub(r'\W+', '-', url).lower()

if __name__ == '__main__':
    import sys
    args     = sys.argv
    test_url = args[1]

    #consumer = SSConsumer(test_url)
    #consumer.environment = DefaultEnvironment()
    #print consumer.consume()

    wizard = SSWizard(test_url)
    wizard.environment = DefaultEnvironment()
    wizard.download()
