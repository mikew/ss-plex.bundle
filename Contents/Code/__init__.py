import string
from ss import Downloader
from ss import util

util.redirect_output('/Users/mike/Work/other/ss-plex.bundle/out')

PLUGIN_PREFIX = '/video/ssp'
PLUGIN_TITLE  = L('title')
PLUGIN_ART    = 'art-default.jpg'
PLUGIN_ICON   = 'icon-default.png'

def Start():
    # Initialize the plug-in
    Plugin.AddViewGroup("Details",  viewMode = "InfoList",  mediaType = "items")
    Plugin.AddViewGroup("List",     viewMode = "List",      mediaType = "items")

    # Setup the default attributes for the ObjectContainer
    ObjectContainer.title1     = PLUGIN_TITLE
    ObjectContainer.view_group = 'List'
    ObjectContainer.art        = R(PLUGIN_ART)

    # Setup the default attributes for the other objects
    DirectoryObject.thumb = R(PLUGIN_ICON)
    DirectoryObject.art   = R(PLUGIN_ART)
    VideoClipObject.thumb = R(PLUGIN_ICON)
    VideoClipObject.art   = R(PLUGIN_ART)

@handler(PLUGIN_PREFIX, PLUGIN_TITLE)
def MainMenu():
    container = render_listings('/')

    favorite_item = DirectoryObject(
        title = 'Favorites',
        key   = Callback(Favorites)
    )

    search_item = InputDirectoryObject(
        key = Callback(SearchResults),
        title = 'Search',
        prompt = 'Search for ...'
    )

    saved_item = DirectoryObject(
        title = 'Saved Searches',
        key   = Callback(SavedSearches)
    )

    container.add(favorite_item)
    container.add(search_item)
    container.add(saved_item)

    return container

@route('%s/search/results' % PLUGIN_PREFIX)
def SearchResults(query):
    container = render_listings('/search/%s' % String.Quote(query))
    save_item = DirectoryObject(
        title = 'Save this search',
        key   = Callback(SaveSearch, query = query)
    )

    container.add(save_item)
    return container

@route('%s/search' % PLUGIN_PREFIX)
def SavedSearches():
    container = ObjectContainer()

    for query in sorted(dict_default('searches', [])):
        item = DirectoryObject(title = query, key = Callback(SearchResults, query = query))
        container.add(item)

    return container

@route('%s/search/save' % PLUGIN_PREFIX)
def SaveSearch(query):
    saved_searches = PluginHelpers.dict_searches()

    if query not in saved_searches:
        saved_searches.append(query)
        Dict.Save()

    return ObjectContainer(header = 'Saved', message = 'Your search has been saved.')

@route('%s/favorites' % PLUGIN_PREFIX)
def Favorites():
    favorites = PluginHelpers.dict_favorites()
    container = ObjectContainer(
        title1 = 'Favorites'
    )

    for endpoint, title in sorted(favorites.iteritems(), key = lambda x:x[1]):
        list_item  = DirectoryObject(
            title = title,
            key   = Callback(ListTVShow, endpoint = endpoint, show_title = title)
        )

        container.add(list_item)

    container.add(DirectoryObject(
        title = 'Clear Favorites',
        key   = Callback(ClearFavorites)
    ))

    return container

@route('%s/favorites/clear' % PLUGIN_PREFIX)
def ClearFavorites():
    del Dict['favorites']
    Dict.Save()
    return ObjectContainer(header = 'Favorites', message = 'Your favorites have been cleared.')

@route('%s/RenderListings' % PLUGIN_PREFIX)
def RenderListings(endpoint, default_title = None):
    return render_listings(endpoint, default_title)

@route('%s/ListSources' % PLUGIN_PREFIX)
def ListSources(endpoint, title, media_hint):
    container     = render_listings(endpoint, default_title = title)
    download_item = DirectoryObject(
        title = 'Download',
        key   = Callback(DownloadsQueue, endpoint = endpoint, media_hint = media_hint)
    )

    container.objects.insert(0, download_item)
    return container

@route('%s/series' % PLUGIN_PREFIX)
def ListTVShow(endpoint, show_title, refresh = 0):
    container = render_listings(endpoint, show_title)
    if 0 < refresh:
        container.replace_parent = True

    if PluginHelpers.show_is_favorite(endpoint):
        favorite_label = '- Remove from Favorites'
    else:
        favorite_label = '+ Add to Favorites'

    favorite_item = DirectoryObject(
        title = favorite_label,
        key   = Callback(ToggleFavorite, endpoint = endpoint, show_title = show_title)
    )

    refresh_item = DirectoryObject(
        title = 'Refresh',
        key   = Callback(ListTVShow, endpoint = endpoint, show_title = show_title, refresh = refresh + 1)
    )

    container.objects.insert(0, favorite_item)
    container.add(refresh_item)

    return container

@route('%s/favorites/toggle' % PLUGIN_PREFIX)
def ToggleFavorite(endpoint, show_title):
    message = None

    if show_is_favorite(endpoint):
        del Dict['favorites'][endpoint]
        message = '%s was removed from your favorites.'
    else:
        favorites             = PluginHelpers.dict_favorites()
        favorites[endpoint]   = show_title
        message               = '%s was added to your favorites.'

    Dict.Save()

    return ObjectContainer(header = 'Favorites', message = message % show_title)

class SSPlexEnvironment:
    def log(self,   message):               Log(message)
    def json(self,  payload_url, **params): return JSON.ObjectFromURL(payload_url, values = params)
    def css(self,   haystack,    selector): return HTML.ElementFromString(haystack).cssselect(selector)
    def xpath(self, haystack,    query):    return HTML.ElementFromString(haystack).xpath(query)

class PluginHelpers(object):
    @classmethod
    def dict_favorites(cls): return cls.initialize_dict('favorites', {})

    @classmethod
    def dict_downloads(cls): return cls.initialize_dict('downloads', [])

    @classmethod
    def dict_searches(cls):  return cls.initialize_dict('searches',  [])

    @classmethod
    def clear_current_download(cls):
        if 'download_current' in Dict:
            del Dict['download_current']
            Dict.Save()

    @classmethod
    def show_is_favorite(cls, endpoint):
        return endpoint in cls.dict_favorites().keys()

    @classmethod
    def initialize_dict(cls, key, default = None):
        if not key in Dict:
            Dict[key] = default

        return Dict[key]

    @classmethod
    def plex_section_destination(cls, section):
        query     = '//Directory[@type="%s"]/Location' % section
        locations = XML.ElementFromURL('http://127.0.0.1:32400/library/sections').xpath(query)
        location  = locations[0].get('path')
        return location

def download_for_endpoint(endpoint):
    """docstring for download_for_endpoint"""
    found = filter(lambda h: h['endpoint'] == endpoint, PluginHelpers.dict_downloads())

    if found:
        return found[0]

@route('%s/downloads' % PLUGIN_PREFIX)
def DownloadsIndex():
    downloads = PluginHelpers.dict_downloads()

@route('%s/downloads/show' % PLUGIN_PREFIX)
def DownloadsShow(endpoint):
    pass

@route('%s/downloads/queue' % PLUGIN_PREFIX)
def DownloadsQueue(endpoint, media_hint):
    Log(download_for_endpoint(endpoint))
    if download_for_endpoint(endpoint):
        return

    PluginHelpers.dict_downloads().append({
        'created_at': Datetime.Now(),
        'endpoint':   endpoint,
        'media_hint': media_hint
    })

    Dict.Save()
    dispatch_download()

@route('%s/downloads/dispatch' % PLUGIN_PREFIX)
def DownloadsDispatch():
    dispatch_download()

@route('%s/downloads/cancel' % PLUGIN_PREFIX)
def DownloadsCancel():
    if 'download_current' in Dict:
        import os, signal
        pid = Dict['download_current'].get('pid')

        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
            except: pass

def dispatch_download(should_thread = True):
    if not 'download_current' in Dict:
        import thread

        def store_curl_pid(dl):
            Dict['download_current']['pid'] = dl.pid
            Dict.Save()

        def clear_current_download(dl):
            PluginHelpers.clear_current_download()
            #HTTP.Request('http://127.0.0.1:32400/video/ssp/downloads/dispatch', immediate = True)
            dispatch_download(False)

        try:
            download = PluginHelpers.dict_downloads().pop(0)
        except IndexError, e:
            #PluginHelpers.clear_current_download()
            return

        Dict['download_current'] = download
        Dict.Save()

        endpoint       = download['endpoint']
        media_hint     = download['media_hint']
        dl             = Downloader(endpoint)
        dl.environment = SSPlexEnvironment()
        dl.destination = PluginHelpers.plex_section_destination(media_hint)

        dl.on_start(store_curl_pid)
        dl.on_success(clear_current_download)
        dl.on_error(clear_current_download)

        if should_thread:
            thread.start_new_thread(dl.download, ())
        else:
            dl.download()

@route('%s/test' % PLUGIN_PREFIX)
def QuickTest():
    return ObjectContainer(header = 'Test', message = 'hello')

@route('%s/reset' % PLUGIN_PREFIX)
def FactoryReset():
    Dict.Reset()

def render_listings(endpoint, default_title = None):
    endpoint = util.listings_endpoint(endpoint)

    Log('Attempting payload from %s' % (endpoint))
    response  = JSON.ObjectFromURL(endpoint)
    container = ObjectContainer(
        title1 = response.get( 'title' ) or default_title,
        title2 = response.get( 'desc' )
    )

    for element in response.get( 'items', [] ):
        naitive          = None
        permalink        = element.get('endpoint')
        display_title    = element.get('display_title') or element.get('title')
        generic_callback = Callback(RenderListings, endpoint = permalink, default_title = display_title)

        if 'endpoint' == element['_type']:
            Log('element is endpoint')
            naitive = DirectoryObject(
                title   = display_title,
                tagline = element.get( 'tagline' ),
                summary = element.get( 'desc' ),
                key     = generic_callback
            )
        elif 'show' == element['_type']:
            Log('element is show')
            naitive = TVShowObject(
                rating_key = permalink,
                title      = display_title,
                summary    = element.get( 'desc' ),
                key        = Callback(ListTVShow, endpoint = permalink, show_title = display_title)
            )
        elif 'movie' == element['_type'] or 'episode' == element['_type']:
            Log('element is playable')
            media_hint = element['_type']
            if 'episode' == media_hint:
                media_hint = 'show'

            naitive = DirectoryObject(
                title = display_title,
                key   = Callback(ListSources, endpoint = permalink, title = display_title, media_hint = media_hint)
            )
        elif 'foreign' == element['_type']:
            Log('element is foreign')
            naitive = DirectoryObject(
                title = element['domain'],
                key   = generic_callback
            )
        elif 'final' == element['_type']:
            Log('element is final')
            ss_url = '//ss/procedure?url=%s&title=%s' % (String.Quote(element['url']), String.Quote('FILE HINT HERE'))
            naitive = VideoClipObject(url = ss_url, title = display_title)

        #elif 'movie' == element['_type']:
            #Log('element is movie')
            #naitive = MovieObject(
                #rating_key = permalink,
                #title      = display_title,
                #tagline    = element.get( 'tagline' ),
                #summary    = element.get( 'desc' ),
                #key        = sources_callback
            #)
        #elif 'episode' == element['_type']:
            #Log('element is episode')
            #naitive = EpisodeObject(
                #rating_key     = permalink,
                #title          = display_title,
                #summary        = element.get( 'desc' ),
                #season         = int( element.get( 'season', 0 ) ),
                #absolute_index = int( element.get( 'number', 0 ) ),
                #key            = sources_callback
            #)

        if None != naitive:
            container.add( naitive )

    return container
