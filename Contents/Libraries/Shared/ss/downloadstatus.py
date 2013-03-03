keys = [
  'percent_total',
  'total_size',
  'percent_segment',
  'total_received',
  'unknown_percent',
  'xferd',
  'average_download',
  'average_upload',
  'time_total',
  'time_spent',
  'time_left',
  'current_speed'
]

def parse_curl(fname):
    values = None
    f = open(fname, 'r')
    f.seek(-100, 2)
    values = f.read().split("\r")[-1].split()
    f.close()

    return values

def parse_wget(fname):
    values = None

    try:
        import re
        f = open(fname, 'r')
        data = f.read()
        f.close()

        status_line      = data.split("\r")[-1]
        status_match     = re.search(r'(\d+)%.*?([0-9A-Za-z]+)/s\s+(?:eta|in) (.+) ', status_line)
        total_size       = re.search(r'^Length: \d+ \((.+)\)', data, re.MULTILINE).group(1)
        percent_total    = status_match.group(1)
        average_download = status_match.group(2)
        eta              = status_match.group(3).strip()

        values = [ percent_total, total_size, percent_total, '?', '?', '?', average_download, 0, '?', '?', eta, average_download ]
    except Exception, e:
        util.print_exception(e)
        pass

    return values

class DownloadStatus(object):
    def __init__(self, fname, strategy = 'curl'):
        super(DownloadStatus, self).__init__()
        self.fname    = fname
        self.parsed   = False
        self.strategy = strategy

    def report_progress(self):
        self.parse_status_file()
        return '%s%% of %s' % (self.percent_total, self.total_size)

    def report_speed(self):
        self.parse_status_file()
        return '%s remaning; %s average.' % (self.time_left, self.average_download)

    def report(self):
        return [ self.report_progress(), self.report_speed() ]

    def file_too_small(self):
        import re

        self.parse_status_file()
        if re.search(r'(k|K|\d|\?)$', self.total_size):
            return True
        else:
            return False

    def parse_status_file(self):
        if self.parsed: return

        try:
            values = globals()['parse_' + self.strategy](self.fname)

            for i, value in enumerate(values):
                setattr(self, keys[i], value)
        except:
            values = [ 0, '?', 0, 0, 0, 0, 0, 0, '?', 0, '?', 0 ]
            for i, value in enumerate(values):
                setattr(self, keys[i], value)

        self.parsed = True

if __name__ == '__main__':
    import sys
    args = sys.argv

    #status = DownloadStatus('curl-status-file', strategy = 'curl')
    #status = DownloadStatus('wget-status-file',           strategy = 'wget')
    status = DownloadStatus('wget-finished-status-file',  strategy = 'wget')
    #status = DownloadStatus('wget-failed-status-file',    strategy = 'wget')
    #status = DownloadStatus('nonexistent')
    for ln in status.report():
        print ln

    print status.file_too_small()
