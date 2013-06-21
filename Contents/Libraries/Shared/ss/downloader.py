import util
from wizard         import Wizard
from downloadstatus import DownloadStatus

log = util.getLogger('ss.downloader')

def curl_strategy_command(dl):
    command = [
        'curl',
        '--location',
        '--referer',    dl.consumer.url,
        '--cookie',     dl.consumer.cookie_string,
        '--user-agent', dl.consumer.ua,
        '--stderr',     dl.status_file,
        '--output',     dl.local_partfile
    ]

    if int(dl.limit) > 0:
        command.append('--limit-rate')
        command.append('%sK' % dl.limit)

    command.append(dl.consumer.asset_url)

    return command

def wget_strategy_command(dl):
    command = [
        'wget',
        '--no-cookies',
        '--continue',
        '--referer',         dl.consumer.url,
        '--header',          'Cookie: ' + dl.consumer.cookie_string,
        '--user-agent',      dl.consumer.ua,
        '--progress',        'bar:force',
        '--output-file',     dl.status_file,
        '--output-document', dl.local_partfile
    ]

    if int(dl.limit) > 0:
        command.append('--limit-rate')
        command.append('%sK' % dl.limit)

    command.append(dl.consumer.asset_url)

    return command

def status_file_for(endpoint):
    import os.path, tempfile
    tmpdir = tempfile.gettempdir()
    status = util.normalize_url(endpoint)
    return os.path.join(tmpdir, status)

def sanitize_file(file_name):
    import re
    encoded  = file_name.encode()
    replaced = re.sub(r'[^a-zA-Z0-9. ]', '', encoded)

    return replaced

def status_for(endpoint, strategy):
    return DownloadStatus(status_file_for(endpoint), strategy = strategy)

class Downloader(object):
    def __init__(self, endpoint, destination = None, limit = 0, strategy = 'curl', avoid_small_files = False):
        self.endpoint    = endpoint
        self.destination = destination
        self.success     = False
        self.limit       = limit
        self.wizard      = Wizard(self.endpoint)
        self.strategy    = strategy
        self.avoid_small = avoid_small_files

        self.init_callbacks()

    @property
    def file_name(self):
        hinted = self.wizard.file_hint.encode()
        consumed = self.consumer.file_name.encode()
        ext = consumed.split('.')[-1]
        merged = '%s.%s' % (hinted, ext)

        return sanitize_file(merged)

    @property
    def status_file(self):
        return status_file_for(self.endpoint)

    @property
    def local_partfile(self):
        return self.local_file + '.part'

    @property
    def local_file(self):
        import os.path
        return os.path.join(self.destination, self.file_name)

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
            try:
                import os
                os.rename( dl.local_partfile, dl.local_file )
            except: pass

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

        command  = self.download_command()
        piped    = subprocess.Popen(command)
        self.pid = piped.pid

        log.info(command)
        self.run_start_callbacks()
        piped.wait()

        returned = abs(piped.returncode)

        if self.avoid_small:
            status = status_for(self.endpoint, strategy = self.strategy)

            if status.file_too_small():
                returned = 99

        if 0 == returned:
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
        self.attempt_remove(self.status_file)

    def cleanup(self):
        self.cleanup_status_file()
        self.attempt_remove(self.local_file)
        self.attempt_remove(self.local_partfile)

    def attempt_remove(self, f):
        import os
        try:    os.remove(f)
        except: pass
