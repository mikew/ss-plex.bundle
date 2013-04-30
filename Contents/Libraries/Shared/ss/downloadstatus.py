defaults = dict(
    percent_total    = 0,
    total_size       = '?',
    percent_segment  = 0,
    total_received   = 0,
    unknown_percent  = 0,
    xferd            = 0,
    average_download = 0,
    average_upload   = 0,
    time_total       = '?',
    time_spent       = 0,
    time_left        = '?',
    current_speed    = 0
)

def parse_curl(fname):
    values = dict()
    keys   = [
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

    f = open(fname, 'r')
    f.seek(-100, 2)
    parts = f.read().split("\r")[-1].split()
    f.close()

    for i, value in enumerate(parts):
        values[keys[i]] = value

    return values

def parse_wget(fname):
    import datetime
    import re

    f = open(fname, 'r')
    data = f.read()
    f.close()

    status_line    = data.split("\r")[-1]
    status_match   = re.search(r'(\d+)%.*?([\d,]+)\s+([0-9A-Za-z.]+)/s\s+(?:eta|in) (.+) ', status_line)
    total_size     = re.search(r'^Length: \d+ \((.+)\)', data, re.MULTILINE).group(1)
    started_match  = re.findall(r'^--([\d\-: ]+)--', data, re.MULTILINE)[-1]
    started        = datetime.datetime.strptime(started_match, '%Y-%m-%d %H:%M:%S')
    now            = datetime.datetime.now()
    delta          = now - started
    elapsed        = (delta.microseconds + (delta.seconds + delta.days * 24 * 3600) * 10**6) / 10**6
    percent_total  = status_match.group(1)
    total_received = int(re.sub(r'[^\d]', '', status_match.group(2))) / 1024
    current_speed  = status_match.group(3)
    eta            = status_match.group(4).strip()

    average_download = str(total_received / elapsed) + ' KB/s'

    return dict(
        percent_total    = percent_total,
        total_size       = total_size,
        percent_segment  = percent_total,
        total_received   = total_received,
        average_download = average_download,
        time_spent       = elapsed,
        time_left        = eta,
        current_speed    = current_speed
    )

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
        return '%s remaining; %s average.' % (self.time_left, self.average_download)

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

            if not values: raise Exception('nothing returned')
            self.set_values(values)
        except:
            self.set_values(defaults)

        self.parsed = True

    def set_values(self, values = None):
        if values: values = dict(defaults.items() + values.items())
        else:      values = defaults

        for key, value in values.iteritems():
            setattr(self, key, value)

if __name__ == '__main__':
    import sys
    args = sys.argv

    #status = DownloadStatus('curl-status-file',           strategy = 'curl')
    status = DownloadStatus('wget-status-file',           strategy = 'wget')
    #status = DownloadStatus('wget-finished-status-file',  strategy = 'wget')
    #status = DownloadStatus('wget-failed-status-file',    strategy = 'wget')
    #status = DownloadStatus('nonexistent')
    for ln in status.report():
        print ln

    print status.file_too_small()
