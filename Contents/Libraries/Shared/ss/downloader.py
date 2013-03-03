import util
#from consumer       import Consumer
from wizard         import Wizard
from downloadstatus import DownloadStatus

import environment

import logging
log = logging.getLogger('ss.downloader')

#util.redirect_output('/Users/mike/Work/other/ss-plex.bundle/out')

def curl_strategy_command(dl):
    command = [
        'curl',
        '--location',
        '--referer',    dl.consumer.url,
        '--cookie',     dl.consumer.agent_cookie_string(),
        '--user-agent', dl.consumer.ua,
        '--stderr',     dl.status_file(),
        '--output',     dl.local_partfile()
    ]

    if int(dl.limit) > 0:
        command.append('--limit-rate')
        command.append('%sK' % dl.limit)

    command.append(dl.asset_url())

    return command

def wget_strategy_command(dl):
    command = [
        'wget',
        '--no-cookies',
        '--referer',         dl.consumer.url,
        '--header',          'Cookie: ' + dl.consumer.agent_cookie_string(),
        '--user-agent',      dl.consumer.ua,
        '--progress',        'bar:force',
        '--output-file',     dl.status_file(),
        '--output-document', dl.local_partfile()
    ]

    if int(dl.limit) > 0:
        command.append('--limit-rate')
        command.append('%sK' % dl.limit)

    command.append(dl.asset_url())

    return command

class Downloader(object):
    def __init__(self, endpoint, environment = environment.default, destination = None, limit = 0, strategy = 'curl'):
        super(Downloader, self).__init__()
        self.endpoint    = endpoint
        self.destination = destination
        self.success     = False
        self.limit       = limit
        self.environment = environment
        self.wizard      = Wizard(self.endpoint, environment = self.environment)
        self.strategy    = strategy

        self.init_callbacks()

    @classmethod
    def status_file_for(cls, endpoint):
        import os.path, tempfile
        tmpdir = tempfile.gettempdir()
        status = util.normalize_url(endpoint)
        return os.path.join(tmpdir, status)

    def file_name(self):
        original = self.consumer.file_name().encode()
        ext      = original.split('.')[-1]
        with_ext = '%s.%s' % (self.file_hint(), ext)

        return self.sanitize_file(with_ext)

    def sanitize_file(self, file_name):
        import re
        encoded  = file_name.encode()
        replaced = re.sub(r'[^a-zA-Z0-9. ]', '', encoded)

        return replaced

    def file_hint(self):
        return self.wizard.file_hint

    def status_file(self):    return Downloader.status_file_for(self.endpoint)
    def asset_url(self):      return self.consumer.asset_url().encode()
    def local_partfile(self): return self.local_file() + '.part'
    def local_file(self):
        import os.path
        return os.path.join(self.destination, self.file_name())

    def add_callback(self, group, cb): self.callbacks[group].append(cb)
    def on_start(self, cb):    self.add_callback('start',    cb)
    def on_success(self,  cb): self.add_callback('success',  cb)
    def on_error(self, cb):    self.add_callback('error',    cb)

    def run_start_callbacks(self):
        log.debug('Running start callbacks')
        self.run_callbacks('_start')
        self.run_callbacks('start')

    def run_success_callbacks(self):
        log.debug('Running success callbacks')
        self.run_callbacks('_success')
        self.run_callbacks('success')

    def run_error_callbacks(self):
        log.debug('Running error callbacks')
        self.run_callbacks('_error')
        self.run_callbacks('error')

    def run_callbacks(self, group):
        for cb in self.callbacks[group]:
            cb(self)

    def init_callbacks(self):
        groups = ( 'start', 'success', 'error' )
        self.callbacks = {}

        for g in groups:
            self.callbacks[g]       = []
            self.callbacks['_' + g] = []

        def rename_partfile(dl):
            import os
            os.rename( dl.local_partfile(), dl.local_file() )

        def cleanup_status_file(dl):
            dl.cleanup_status_file()

        self.add_callback('_success', rename_partfile)
        self.add_callback('_success', cleanup_status_file)

    def download(self):
        def perform_download(consumer):
            self.consumer = consumer
            self.success  = self.really_download()

        self.wizard.sources(perform_download)

        if self.success:
            self.run_success_callbacks()
            log.info('Finished downloading %s' % self.wizard.file_hint)
        else:
            self.run_error_callbacks()

    def download_command(self):
        return globals()[self.strategy + '_strategy_command'](self)

    def really_download(self):
        from signal import SIGTERM
        import subprocess
        import re

        options = self.curl_options()
        log.info(options)
        piped    = subprocess.Popen(options)
        self.pid = piped.pid

        self.run_start_callbacks()
        piped.wait()

        returned = abs(piped.returncode)
        status   = DownloadStatus(self.status_file())
        status.parse_status_file()

        if re.search(r'(k|K|\d)$', status.total_size):
            returned = 99

        if 0 == returned:
            log.info('Download finished in %s, average %s' % (status.time_total, status.average_download))
            return True
        elif SIGTERM == returned:
            log.info('SIGTERM received, download will abort')
            self.cleanup()
            return False
        else:
            log.info('%s received, trying next source' % returned)
            self.cleanup()
            raise Exception('cURL returned %s, trying next source.' % returned)

    def cleanup_status_file(self):
        self.attempt_remove(self.status_file())

    def cleanup(self):
        self.cleanup_status_file()
        self.attempt_remove(self.local_file())
        self.attempt_remove(self.local_partfile())

    def attempt_remove(self, f):
        import os
        try:    os.remove(f)
        except: pass

if __name__ == '__main__':
    util.log_to_stderr()
    import os, sys
    args     = sys.argv
    test_url = args[1]

    def start(dl):   print 'start'
    def success(dl): print 'success'
    def error(dl):   print 'error'

    dl = Downloader(test_url, destination = os.getcwd())

    dl.on_start(start)
    dl.on_success(success)
    dl.on_error(error)

    dl.download()
