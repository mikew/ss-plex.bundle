# -*- coding: UTF-8 -*-

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

class DownloadStatus(object):
    def __init__(self, fname):
        super(DownloadStatus, self).__init__()
        self.fname  = fname
        self.parsed = False

    def report_progress(self):
        self.parse_status_file()
        return '%s%% of %s' % (self.percent_total, self.total_size)

    def report_speed(self):
        self.parse_status_file()
        return '%s remaning; %s average.' % (self.time_left, self.average_download)

    def report(self):
        return [ self.report_progress(), self.report_speed() ]

    def parse_status_file(self):
        if self.parsed: return

        try:
            f = open(self.fname, 'r')
            f.seek(-100, 2)
            values = f.read().split("\r")[-1].split()
            f.close()
        except:
            values = [ 0, '?', 0, 0, 0, 0, 0, 0, u'∞', 0, u'∞', 0 ]

        for i, value in enumerate(values):
            setattr(self, keys[i], value)

        self.parsed = True

if __name__ == '__main__':
    import sys
    args = sys.argv

    status = DownloadStatus('curl-status-file')
    #status = DownloadStatus('zcurl-status-file')
    for ln in status.report():
        print ln
