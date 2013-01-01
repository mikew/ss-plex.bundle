import plex
import user

def clear():            user.attempt_clear('favorites2')
def includes(endpoint): return endpoint in collection()
def collection():       return user.initialize_dict('favorites2', {})

def append(**k):
    endpoint = k['endpoint']
    del k['endpoint']
    collection()[endpoint] = k
    plex.user_dict().Save()

def remove(endpoint):
    del collection()[endpoint]
    plex.user_dict().Save()
