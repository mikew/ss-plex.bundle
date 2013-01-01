import plex
import user

def clear():      user.attempt_clear('searches')
def includes(q):  return q in collection()
def collection(): return user.initialize_dict('searches', [])

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

    plex.user_dict().Save()
    return response

def append(q):
    collection().append(q)
    plex.user_dict().Save()

def remove(q):
    collection().remove(q)
    plex.user_dict().Save()

