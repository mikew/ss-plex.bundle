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
        self.fname = fname

    def report(self):
        self.parse_status_file()
        return '%s remaning at an average of %s.' % (self.time_left, self.average_download)

    def parse_status_file(self):
      f = open(self.fname, 'r')
      f.seek(-100, 2)
      values = f.read().split("\r")[-1].split()
      f.close()

      for i, value in enumerate(values):
          setattr(self, keys[i], value)

if __name__ == '__main__':
    import sys
    args = sys.argv

    status = DownloadStatus('curl-status-file')
    print status.report()
