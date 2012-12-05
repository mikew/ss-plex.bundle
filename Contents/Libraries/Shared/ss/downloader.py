from consumer import Consumer, DefaultEnvironment
from wizard   import Wizard
import util

#util.redirect_output('/Users/mike/Work/other/ss-plex.bundle/out')

class Downloader(object):
    def __init__(self, endpoint, environment = None, destination = None, limit = 0):
        super(Downloader, self).__init__()
        self.endpoint    = endpoint
        self.destination = destination
        self.success     = False
        self.limit       = limit
        self.environment = environment
        if not self.environment: self.environment = DefaultEnvironment()
        self.wizard      = Wizard(self.endpoint, environment = self.environment)

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

        return '%s.%s' % (self.file_hint(), ext)

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
        self.run_callbacks('_start')
        self.run_callbacks('start')

    def run_success_callbacks(self):
        self.run_callbacks('_success')
        self.run_callbacks('success')

    def run_error_callbacks(self):
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

        def debug_dl(dl):
            lines = [ dl.pid, dl.consumer.url, dl.asset_url(), dl.local_file() ]

            for line in lines:
                self.environment.log(line)

        def rename_partfile(dl):
            import os
            os.rename( dl.local_partfile(), dl.local_file() )

        def cleanup_status_file(dl):
            dl.cleanup_status_file()

        #self.add_callback('_start',   debug_dl)
        self.add_callback('_success', rename_partfile)
        self.add_callback('_success', cleanup_status_file)

    def download(self):
        def perform_download(consumer):
            self.consumer = consumer
            self.success  = self.really_download()

        self.wizard.sources(perform_download)

        if self.success:
            self.run_success_callbacks()
        else:
            self.run_error_callbacks()

    def curl_options(self):
        options = [
            'curl',
            '--referer',    self.consumer.url,
            '--cookie',     self.consumer.agent_cookie_string(),
            '--user-agent', self.consumer.ua,
            '--stderr',     self.status_file(),
            '--output',     self.local_partfile()
        ]

        if int(self.limit) > 0:
            options.append('--limit-rate')
            options.append('%sK' % self.limit)

        options.append(self.asset_url())

        return options

    def really_download(self):
        from signal import SIGTERM
        import subprocess

        piped    = subprocess.Popen(self.curl_options())
        self.pid = piped.pid

        self.run_start_callbacks()
        piped.wait()

        returned = abs(piped.returncode)
        if 0 == returned:
            return True
        elif SIGTERM == returned:
            self.cleanup()
            return False
        else:
            self.cleanup()
            raise

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
