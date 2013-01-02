import user

class PlexDictStore(object):
    def __init__(self):
        super(PlexDictStore, self).__init__()
        self._store = user.initialize_dict('cache', {})

    def set(self, key, value, **options):
        store = self._store

        store[key]            = {}
        store[key]['expires'] = Datetime.TimestampFromDatetime(Datetime.Now()) + options['expires']
        store[key]['value']   = value
        Dict.Save()

    def get(self, key, **k):
        return self._store[key]['value']

    def exists(self, key, **k):
        return key in self._store

    def expired(self, key, **k):
        return int(self._store[key]['expires']) < Datetime.TimestampFromDatetime(Datetime.Now())
