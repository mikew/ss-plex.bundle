import string
from ss import Downloader
from ss import util
from ss import DownloadStatus

#util.redirect_output('/Users/mike/Work/other/ss-plex.bundle/out')

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
    container   = render_listings('/')
    search_item = plobj(InputDirectoryObject, 'Search', SearchResults)
    search_item.prompt = 'Search for ...'

    container.add(plobj(DirectoryObject, 'Favorites', FavoritesIndex))
    container.add(search_item)
    container.add(plobj(DirectoryObject, 'Saved Searches', SearchIndex))
    container.add(plobj(DirectoryObject, 'Downloads', DownloadsIndex))

    return container

#############
# Searching #
#############

@route('%s/search' % PLUGIN_PREFIX)
def SearchIndex():
    container = ObjectContainer()

    for query in sorted(PluginHelpers.dict_searches()):
        container.add(plobj(DirectoryObject, query, SearchResults, query = query))

    return container

@route('%s/search/results/{query}' % PLUGIN_PREFIX)
def SearchResults(query):
    container = render_listings('/search/%s' % util.q(query))
    container.add(plobj(DirectoryObject, 'Save this search', SearchSave, query = query))
    return container

@route('%s/search/save' % PLUGIN_PREFIX)
def SearchSave(query):
    saved_searches = PluginHelpers.dict_searches()

    if query not in saved_searches:
        saved_searches.append(query)
        Dict.Save()

    return dialog('Saved', 'Your search has been saved.')

#############
# Favorites #
#############

@route('%s/favorites' % PLUGIN_PREFIX)
def FavoritesIndex():
    favorites = PluginHelpers.dict_favorites()
    container = ObjectContainer(
        title1 = 'Favorites'
    )

    for endpoint, title in sorted(favorites.iteritems(), key = lambda x:x[1]):
        container.add(plobj(DirectoryObject, title, ListTVShow, endpoint = endpoint, show_title = title))

    container.add(plobj(DirectoryObject, 'Clear Favorites', FavoritesClear))

    return container

@route('%s/favorites/toggle' % PLUGIN_PREFIX)
def FavoritesToggle(endpoint, show_title):
    message = None

    if PluginHelpers.show_is_favorite(endpoint):
        del Dict['favorites'][endpoint]
        message = '%s was removed from your favorites.'
    else:
        favorites             = PluginHelpers.dict_favorites()
        favorites[endpoint]   = show_title
        message               = '%s was added to your favorites.'

    Dict.Save()

    return dialog('Favorites', message % show_title)

@route('%s/favorites/clear' % PLUGIN_PREFIX)
def FavoritesClear():
    del Dict['favorites']
    Dict.Save()

    return ObjectContainer(header = 'Favorites', message = 'Your favorites have been cleared.')

###############
# Downloading #
###############

@route('%s/downloads' % PLUGIN_PREFIX)
def DownloadsIndex():
    container = ObjectContainer(title1 = 'Downloads')

    if PluginHelpers.currently_downloading():
        current       = Dict['download_current']
        endpoint      = current['endpoint']
        status        = DownloadStatus(Downloader.status_file_for(endpoint))

        container.add(plobj(DirectoryObject, current['title'], DownloadsShow, endpoint = 'current'))

        for ln in status.report():
            container.add(plobj(DirectoryObject, ln, DownloadsShow, endpoint = 'current'))

    for download in PluginHelpers.dict_downloads():
        container.add(plobj(DirectoryObject, download['title'], DownloadsShow, endpoint = download['endpoint']))

    return container

@route('%s/downloads/show' % PLUGIN_PREFIX)
def DownloadsShow(endpoint):
    download = PluginHelpers.download_for_endpoint(endpoint)

    if download:
        container = ObjectContainer(title1 = download['title'])

        if 'current' == endpoint:
            container.add(plobj(DirectoryObject, 'Try Next', DownloadsNext))
            container.add(plobj(DirectoryObject, 'Cancel',   DownloadsCancel, endpoint = 'current'))
        else:
            container.add(plobj(DirectoryObject, 'Cancel', DownloadsCancel, endpoint = endpoint))

        return container
    else:
        return dialog('Whoops', 'No download found for %s.' % endpoint)

@route('%s/downloads/queue' % PLUGIN_PREFIX)
def DownloadsQueue(endpoint, media_hint, title):
    if PluginHelpers.has_downloaded(endpoint):
        message = '%s is already in your library.'
    else:
        message = '%s will be downloaded shortly.'
        PluginHelpers.dict_downloads().append({
            'title':      title,
            'endpoint':   endpoint,
            'media_hint': media_hint
        })

        PluginHelpers.download_history().append(endpoint)

        Dict.Save()

    PluginHelpers.dispatch_download()
    return dialog('Downloads', message % title)

@route('%s/downloads/dispatch' % PLUGIN_PREFIX)
def DownloadsDispatch():
    PluginHelpers.dispatch_download()

@route('%s/downloads/dispatch/force' % PLUGIN_PREFIX)
def DownloadsDispatchForce():
    PluginHelpers.clear_current_download()
    PluginHelpers.dispatch_download()

@route('%s/downloads/cancel' % PLUGIN_PREFIX)
def DownloadsCancel(endpoint):
    download = PluginHelpers.download_for_endpoint(endpoint)

    if download:
        if 'current' == endpoint:
            PluginHelpers.signal_download('cancel')
        else:
            try:
                PluginHelpers.dict_downloads().remove(download)
                Dict.Save()
            except: pass

        return dialog('Downloads', '%s has been cancelled.' % download['title'])
    else:
        return dialog('Whoops', 'No download found for %s.' % endpoint)

@route('%s/downloads/next' % PLUGIN_PREFIX)
def DownloadsNext():
    PluginHelpers.signal_download('next')

#########################
# Development Endpoints #
#########################

@route('%s/test' % PLUGIN_PREFIX)
def QuickTest():
    return ObjectContainer(header = 'Test', message = 'hello')

@route('%s/reset' % PLUGIN_PREFIX)
def FactoryReset():
    Dict.Reset()
    #Dict.Save()

###################
# Listing Methods #
###################

@route('%s/RenderListings' % PLUGIN_PREFIX)
def RenderListings(endpoint, default_title = None):
    return render_listings(endpoint, default_title)

@route('%s/WatchOptions' % PLUGIN_PREFIX)
def WatchOptions(endpoint, title, media_hint):
    container        = render_listings(endpoint, default_title = title)

    wizard_url       = '//ss/wizard?endpoint=%s' % endpoint
    wizard_item      = VideoClipObject(title = 'Watch Now', url = wizard_url)

    sources_endpoint = util.sources_endpoint(endpoint, True)
    sources_item     = plobj(DirectoryObject, 'View all Sources', RenderListings, endpoint = sources_endpoint, default_title = title)

    if PluginHelpers.has_downloaded(endpoint):
        download_item = plobj(DirectoryObject, 'Already in library.', DownloadsShow, endpoint = endpoint)
    else:
        download_item = plobj(DirectoryObject, 'Watch Later', DownloadsQueue,
            endpoint   = endpoint,
            media_hint = media_hint,
            title      = title
        )

    container.objects.insert(0, wizard_item)
    container.objects.insert(1, download_item)
    container.objects.insert(2, sources_item)

    return container

@route('%s/series/{refresh}' % PLUGIN_PREFIX)
def ListTVShow(endpoint, show_title, refresh = 0):
    container = render_listings(endpoint, show_title)
    if 0 < refresh:
        container.replace_parent = True

    if PluginHelpers.show_is_favorite(endpoint): favorite_label = '- Remove from Favorites'
    else:                                        favorite_label = '+ Add to Favorites'

    container.objects.insert(0, plobj(DirectoryObject, favorite_label, FavoritesToggle,
        endpoint   = endpoint,
        show_title = show_title
    ))

    container.add(plobj(DirectoryObject, 'Refresh', ListTVShow,
        endpoint   = endpoint,
        show_title = show_title,
        refresh    = refresh + 1
    ))

    return container

def render_listings(endpoint, default_title = None):
    endpoint = util.listings_endpoint(endpoint)

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
            naitive = DirectoryObject(
                title   = display_title,
                tagline = element.get( 'tagline' ),
                summary = element.get( 'desc' ),
                key     = generic_callback
            )
        elif 'show' == element['_type']:
            naitive = TVShowObject(
                rating_key = permalink,
                title      = display_title,
                summary    = element.get( 'desc' ),
                key        = Callback(ListTVShow, endpoint = permalink, show_title = display_title)
            )
        elif 'movie' == element['_type'] or 'episode' == element['_type']:
            media_hint = element['_type']
            if 'episode' == media_hint:
                media_hint = 'show'

            naitive = PopupDirectoryObject(
                title = display_title,
                key   = Callback(WatchOptions, endpoint = permalink, title = display_title, media_hint = media_hint)
            )
        elif 'foreign' == element['_type']:
            foreign_url = '//ss%s' % util.translate_endpoint(element['original_url'], element['foreign_url'], True)
            naitive = VideoClipObject(title = element['domain'], url = foreign_url)
        elif 'final' == element['_type']:
            ss_url = '//ss/procedure?url=%s&title=%s' % (util.q(element['url']), util.q('FILE HINT HERE'))
            naitive = VideoClipObject(url = ss_url, title = display_title)

        #elif 'movie' == element['_type']:
            #naitive = MovieObject(
                #rating_key = permalink,
                #title      = display_title,
                #tagline    = element.get( 'tagline' ),
                #summary    = element.get( 'desc' ),
                #key        = sources_callback
            #)
        #elif 'episode' == element['_type']:
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

#######################
# SS Plex Environment #
#######################

class SSPlexEnvironment:
    def log(self,   message):               Log(message)
    def json(self,  payload_url, **params): return JSON.ObjectFromURL(payload_url, values = params)
    def css(self,   haystack,    selector): return HTML.ElementFromString(haystack).cssselect(selector)
    def xpath(self, haystack,    query):    return HTML.ElementFromString(haystack).xpath(query)

##################
# Plugin Helpers #
##################

class PluginHelpers(object):
    @classmethod
    def dict_favorites(cls): return cls.initialize_dict('favorites', {})

    @classmethod
    def dict_downloads(cls): return cls.initialize_dict('downloads', [])

    @classmethod
    def dict_searches(cls):  return cls.initialize_dict('searches',  [])

    @classmethod
    def download_history(cls): return cls.initialize_dict('download_history', [])

    @classmethod
    def currently_downloading(cls): return 'download_current' in Dict

    @classmethod
    def has_downloaded(cls, endpoint): return endpoint in cls.download_history()

    @classmethod
    def show_is_favorite(cls, endpoint): return endpoint in cls.dict_favorites().keys()

    @classmethod
    def clear_current_download(cls):
        if cls.currently_downloading(): del Dict['download_current']
        Dict.Save()

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

    @classmethod
    def download_for_endpoint(cls, endpoint):
        if 'current' == endpoint:
            if cls.currently_downloading():
                return Dict['download_current']
        else:
            found = filter(lambda h: h['endpoint'] == endpoint, cls.dict_downloads())

            if found:
                return found[0]

    @classmethod
    def signal_download(cls, sig):
        if cls.currently_downloading():
            import os, signal

            signals = [ signal.SIGTERM, signal.SIGINT ]
            names   = [ 'cancel',       'next' ]
            to_send = signals[names.index(sig)]
            pid     = Dict['download_current'].get('pid')

            if pid:
                try:
                    if 'nt' == os.name:
                        import ctypes
                        # 1 == PROCESS_TERMINATE
                        handle = ctypes.windll.kernel32.OpenProcess(1, False, pid)
                        ctypes.windll.kernel32.TerminateProcess(handle, to_send * -1)
                        ctypes.windll.kernel32.CloseHandle(handle)
                    else:
                        os.kill(pid, to_send)
                except Exception, e:
                    pass

    @classmethod
    def dispatch_download(cls, should_thread = True):
        if not cls.currently_downloading():
            import thread

            try:
                download = cls.dict_downloads().pop(0)
            except IndexError, e:
                return

            Dict['download_current'] = download
            Dict.Save()

            downloader = Downloader(download['endpoint'],
                environment = SSPlexEnvironment(),
                destination = cls.plex_section_destination(download['media_hint'])
            )

            def store_curl_pid(dl):
                Dict['download_current']['title'] = dl.file_name()
                Dict['download_current']['pid']   = dl.pid
                Dict.Save()

            def update_library(dl):
                plex_refresh_section(download['media_hint'])

            def clear_download_and_dispatch(dl):
                cls.clear_current_download()
                cls.dispatch_download(False)

            def remove_endpoint_from_history(dl):
                cls.download_history().remove(dl.endpoint)
                Dict.Save()

            downloader.on_start(store_curl_pid)

            downloader.on_success(update_library)
            downloader.on_success(clear_download_and_dispatch)

            downloader.on_error(remove_endpoint_from_history)
            downloader.on_error(clear_download_and_dispatch)

            #thread.start_new_thread(downloader.download, ())

            if should_thread:
                thread.start_new_thread(downloader.download, ())
            else:
                downloader.download()

def plobj(obj, otitle, cb, **kwargs): return obj(title = otitle, key = Callback(cb, **kwargs))
def dialog(title, message):           return ObjectContainer(header = title, message = message)

def plex_refresh_section(section):
    base    = 'http://127.0.0.1:32400/library/sections'
    query   = '//Directory[@type="%s"]' % section
    element = XML.ElementFromURL(base).xpath(query)[0]
    key     = element.get('key')
    url     = base + '/%s/refresh' % key

    HTTP.Request(url, immediate = True)
