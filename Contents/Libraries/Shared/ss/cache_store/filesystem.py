class FileSystem(object):
    def __init__(self):
        super(FileSystem, self).__init__()

    def local_file(self, key):
        import inspect, os
        return os.path.abspath(inspect.getfile(inspect.currentframe()) + '/../../tmp/%s' % self.normalize_key(key))

    def normalize_key(self, key):
        import re
        return re.sub(r'\W+', '-', key).lower().encode()

    def exists(self, key, **k):
        import os
        return os.path.exists(self.local_file(key))

    def expired(self, key, **k):
        import datetime, time, os
        try:
            now      = time.mktime(datetime.datetime.now().timetuple())
            modified = os.path.getmtime(self.local_file(key))
            delta    = now - modified

            return k['expires'] < delta
        except:
            return True

    def get(self, key, **k):
        f    = open(self.local_file(key))
        data = f.read()
        f.close()

        return data

    def set(self, key, value, **k):
        local = open(self.local_file(key), 'w')
        local.write(value)
        local.close()
