store = None
def set(key, value):          return store.set(key, value)
def get(key, default = None): return store.get(key, default)
def clear(key):               return store.clear(key)
def persist():                return store.persist()
