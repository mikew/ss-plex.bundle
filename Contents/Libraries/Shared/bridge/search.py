import settings

def clear():      settings.clear('searches')
def includes(q):  return q in collection()
def collection(): return settings.get('searches', [])

def toggle(q):
    try:
        if includes(q):
            remove(q)
            response = 'removed'
        else:
            append(q)
            response = 'added'
    except Exception, e:
        return 'error'

    return response

def append(q):
    collection().append(q)
    settings.persist()

def remove(q):
    collection().remove(q)
    settings.persist()
