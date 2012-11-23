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
    #ObjectContainer.title1     = PLUGIN_TITLE
    ObjectContainer.view_group = 'List'
    #ObjectContainer.art        = R(PLUGIN_ART)

    # Setup the default attributes for the other objects
    #DirectoryObject.thumb = R(PLUGIN_ICON)
    #DirectoryObject.art   = R(PLUGIN_ART)
    #VideoClipObject.thumb = R(PLUGIN_ICON)
    #VideoClipObject.art   = R(PLUGIN_ART)

@handler(PLUGIN_PREFIX, PLUGIN_TITLE)
def MainMenu():
    container   = render_listings('/')
    search_item = plobj(InputDirectoryObject, L('heading.search'),    SearchResults)
    search_item.prompt = L('search.prompt')

    container.add(plobj(DirectoryObject, L('heading.favorites'),      FavoritesIndex))
    container.add(search_item)
    container.add(plobj(DirectoryObject, L('search.heading.saved'), SearchIndex))
    container.add(plobj(DirectoryObject, L('heading.download'),     DownloadsIndex))
    container.add(plobj(DirectoryObject, L('heading.system'),       SystemIndex))

    return container

##########
# System #
##########

@route('%s/system' % PLUGIN_PREFIX)
def SystemIndex():
    container = ObjectContainer(title1 = L('heading.system'))

    container.add(confirm(L('system.heading.reset-favorites'),               SystemConfirmResetFavorites))
    container.add(confirm(L('system.heading.reset-search'),                  SystemConfirmResetSearches))
    container.add(confirm(L('system.heading.reset-download-history'),        SystemConfirmResetDownloads))
    container.add(confirm(L('system.heading.reset-factory'),                 SystemConfirmResetFactory))
    container.add(plobj(DirectoryObject, L('system.heading.dispatch-force'), DownloadsDispatchForce))

    return container

@route('%s/system/confirm/reset-favorites' % PLUGIN_PREFIX)
def SystemConfirmResetFavorites(): return warning(L('system.warning.reset-favorites'), L('confirm.yes'), SystemResetFavorites)

@route('%s/system/confirm/reset-searches' % PLUGIN_PREFIX)
def SystemConfirmResetSearches(): return warning(L('system.warning.reset-search'), L('confirm.yes'), SystemResetSearches)

@route('%s/system/confirm/reset-downloads' % PLUGIN_PREFIX)
def SystemConfirmResetDownloads(): return warning(L('system.warning.reset-download-history'), L('confirm.yes'), SystemResetDownloads)

@route('%s/system/confirm/reset-factory' % PLUGIN_PREFIX)
def SystemConfirmResetFactory(): return warning(L('system.warning.reset-factory'), L('confirm.yes'), SystemResetFactory)

@route('%s/system/reset/favorites' % PLUGIN_PREFIX)
def SystemResetFavorites():
    User.clear_favorites()
    return dialog(L('heading.system'), L('system.response.reset-favorites'))

@route('%s/system/reset/searches' % PLUGIN_PREFIX)
def SystemResetSearches():
    User.clear_searches()
    return dialog(L('heading.system'), L('system.response.reset-search'))

@route('%s/system/reset/downloads' % PLUGIN_PREFIX)
def SystemResetDownloads():
    User.clear_download_history()
    return dialog(L('heading.system'), L('system.response.reset-download-history'))

@route('%s/system/reset/factory' % PLUGIN_PREFIX)
def SystemResetFactory():
    Dict.Reset()
    return dialog(L('heading.system'), L('system.response.reset-factory'))

#############
# Searching #
#############

@route('%s/search' % PLUGIN_PREFIX)
def SearchIndex():
    container = ObjectContainer()

    for query in sorted(User.searches()):
        container.add(plobj(DirectoryObject, query, SearchResults, query = query))

    return container

@route('%s/search/results/{query}' % PLUGIN_PREFIX)
def SearchResults(query):
    container = render_listings('/search/%s' % util.q(query))
    container.add(plobj(DirectoryObject, L('search.heading.save'), SearchSave, query = query))
    return container

@route('%s/search/save' % PLUGIN_PREFIX)
def SearchSave(query):
    saved_searches = User.searches()

    if query not in saved_searches:
        saved_searches.append(query)
        Dict.Save()

    return dialog(L('heading.search'), L('search.response.added'))

#############
# Favorites #
#############

@route('%s/favorites' % PLUGIN_PREFIX)
def FavoritesIndex():
    favorites = User.favorites()
    container = ObjectContainer(
        title1 = 'Favorites'
    )

    for endpoint, title in sorted(favorites.iteritems(), key = lambda x:x[1]):
        container.add(plobj(DirectoryObject, title, ListTVShow, endpoint = endpoint, show_title = title))

    return container

@route('%s/favorites/toggle' % PLUGIN_PREFIX)
def FavoritesToggle(endpoint, show_title):
    message = None

    if User.endpoint_is_favorite(endpoint):
        del Dict['favorites'][endpoint]
        message = 'favorites.response.removed'
    else:
        favorites           = User.favorites()
        favorites[endpoint] = show_title
        message             = 'favorites.response.added'

    Dict.Save()

    return dialog(L('heading.favorites'), F(message, show_title))

###############
# Downloading #
###############

@route('%s/downloads' % PLUGIN_PREFIX)
def DownloadsIndex():
    container = ObjectContainer(title1 = L('heading.download'))

    if User.currently_downloading():
        current       = Dict['download_current']
        endpoint      = current['endpoint']
        status        = DownloadStatus(Downloader.status_file_for(endpoint))

        container.add(plobj(PopupDirectoryObject, current['title'], DownloadsOptions, endpoint = endpoint))

        for ln in status.report():
            container.add(plobj(PopupDirectoryObject, ln, DownloadsOptions, endpoint = endpoint))

    for download in User.download_queue():
        container.add(plobj(PopupDirectoryObject, download['title'], DownloadsOptions, endpoint = download['endpoint']))

    return container

@route('%s/downloads/show' % PLUGIN_PREFIX)
def DownloadsOptions(endpoint):
    download = User.download_for_endpoint(endpoint)

    if download:
        container  = ObjectContainer(title1 = download['title'])
        obj_cancel = plobj(DirectoryObject, L('download.heading.cancel'), DownloadsCancel, endpoint = endpoint)

        if User.endpoint_is_downloading(endpoint):
            if not User.pid_running(Dict['download_current']['pid']):
                container.add(plobj(DirectoryObject, L('download.heading.repair'), DownloadsDispatchForce))
            else:
                container.add(plobj(DirectoryObject, L('download.heading.next'), DownloadsNext))
                container.add(obj_cancel)
        else:
            container.add(obj_cancel)

        return container
    else:
        return dialog(L('heading.error'), F('download.response.not-found', endpoint))

@route('%s/downloads/queue' % PLUGIN_PREFIX)
def DownloadsQueue(endpoint, media_hint, title):
    if User.has_downloaded(endpoint):
        message = 'download.response.exists'
    else:
        message = 'download.response.added'
        User.download_queue().append({
            'title':      title,
            'endpoint':   endpoint,
            'media_hint': media_hint
        })

        Dict.Save()

    User.dispatch_download()
    return dialog(L('heading.download'), F(message, title))

@route('%s/downloads/dispatch' % PLUGIN_PREFIX)
def DownloadsDispatch():
    User.dispatch_download()

@route('%s/downloads/dispatch/force' % PLUGIN_PREFIX)
def DownloadsDispatchForce():
    User.clear_current_download()
    User.dispatch_download()

@route('%s/downloads/cancel' % PLUGIN_PREFIX)
def DownloadsCancel(endpoint):
    download = User.download_for_endpoint(endpoint)

    if download:
        if User.endpoint_is_downloading(endpoint):
            User.signal_download('cancel')
        else:
            try:
                User.download_queue().remove(download)
                Dict.Save()
            except: pass

        return dialog(L('heading.download'), F('download.response.cancel', download['title']))
    else:
        return dialog(L('heading.error'), F('download.response.not-found', endpoint))

@route('%s/downloads/next' % PLUGIN_PREFIX)
def DownloadsNext():
    User.signal_download('next')

#########################
# Development Endpoints #
#########################

@route('%s/test' % PLUGIN_PREFIX)
def QuickTest():
    return ObjectContainer(header = 'Test', message = 'hello')

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
    wizard_item      = VideoClipObject(title = L('media.watch-now'), url = wizard_url)

    sources_endpoint = util.sources_endpoint(endpoint, True)
    sources_item     = plobj(DirectoryObject, L('media.all-sources'), RenderListings, endpoint = sources_endpoint, default_title = title)

    if User.has_downloaded(endpoint):
        download_item = plobj(DirectoryObject, L('media.persisted'), DownloadsOptions, endpoint = endpoint)
    else:
        download_item = plobj(DirectoryObject, L('media.watch-later'), DownloadsQueue,
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
    refresh   = int(refresh)
    container = render_listings(endpoint, show_title)

    if 0 < refresh:
        container.replace_parent = True

    if User.endpoint_is_favorite(endpoint): favorite_label = 'favorites.heading.remove'
    else:                                   favorite_label = 'favorites.heading.add'

    container.objects.insert(0, plobj(DirectoryObject, L(favorite_label), FavoritesToggle,
        endpoint   = endpoint,
        show_title = show_title
    ))

    container.add(plobj(DirectoryObject, L('heading.refresh'), ListTVShow,
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

class User(object):
    @classmethod
    def favorites(cls): return cls.initialize_dict('favorites', {})

    @classmethod
    def searches(cls): return cls.initialize_dict('searches',  [])

    @classmethod
    def download_queue(cls): return cls.initialize_dict('downloads', [])

    @classmethod
    def download_history(cls): return cls.initialize_dict('download_history', [])

    @classmethod
    def currently_downloading(cls): return 'download_current' in Dict

    @classmethod
    def endpoint_is_favorite(cls, endpoint): return endpoint in cls.favorites().keys()

    @classmethod
    def clear_favorites(cls): cls.attempt_clear('favorites')

    @classmethod
    def clear_searches(cls): cls.attempt_clear('searches')

    @classmethod
    def clear_download_history(cls): cls.attempt_clear('download_history')

    @classmethod
    def clear_current_download(cls): cls.attempt_clear('download_current')

    @classmethod
    def running_windows(cls):
        import os
        return 'nt' == os.name

    @classmethod
    def pid_running(cls, pid):
        if cls.running_windows():
            return cls.pid_running_windows(pid)
        else:
            return cls.signal_process_unix(pid)

    @classmethod
    def signal_process(cls, pid, to_send = 0):
        if cls.running_windows():
            return cls.signal_process_windows(pid, to_send)
        else:
            return cls.signal_process_unix(pid, to_send)

    @classmethod
    def signal_process_unix(cls, pid, to_send = 0):
        try:
            import os
            os.kill(pid, to_send)
            return True
        except:
            return False

    @classmethod
    def signal_process_windows(cls, pid, to_send = 0):
        try:
            import ctypes
            # 1 == PROCESS_TERMINATE
            handle = ctypes.windll.kernel32.OpenProcess(1, False, pid)
            ctypes.windll.kernel32.TerminateProcess(handle, to_send * -1)
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        except:
            return False

    @classmethod
    def pid_running_windows(cls, pid):
        import ctypes, ctypes.wintypes
        # GetExitCodeProcess uses a special exit code to indicate that the process is
        # still running.
        still_active = 259
        kernel32     = ctypes.windll.kernel32
        handle       = kernel32.OpenProcess(1, 0, pid)

        if handle == 0:
            return False

        # If the process exited recently, a pid may still exist for the handle.
        # So, check if we can get the exit code.
        exit_code  = ctypes.wintypes.DWORD()
        is_running = ( kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)) == 0 )
        kernel32.CloseHandle(handle)

        # See if we couldn't get the exit code or the exit code indicates that the
        # process is still running.
        return is_running or exit_code.value == still_active

    @classmethod
    def attempt_clear(cls, key):
        if key in Dict:
            del Dict[key]
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
    def endpoint_is_downloading(cls, endpoint):
        return cls.currently_downloading() and endpoint == Dict['download_current']['endpoint']

    @classmethod
    def has_downloaded(cls, endpoint):
        found = cls.download_for_endpoint(endpoint)

        if found: return True
        else:     return endpoint in cls.download_history()

    @classmethod
    def download_for_endpoint(cls, endpoint):
        if cls.endpoint_is_downloading(endpoint):
            return Dict['download_current']
        else:
            found = filter(lambda h: h['endpoint'] == endpoint, cls.download_queue())

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
                return cls.signal_process(pid, to_send)

    @classmethod
    def dispatch_download(cls, should_thread = True):
        if not cls.currently_downloading():
            import thread

            try:
                download = cls.download_queue().pop(0)
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

            def store_download_endpoint(dl):
                cls.download_history().append(dl.endpoint)

            downloader.on_start(store_curl_pid)

            downloader.on_success(update_library)
            downloader.on_success(store_download_endpoint)
            downloader.on_success(clear_download_and_dispatch)

            downloader.on_error(clear_download_and_dispatch)

            if should_thread:
                thread.start_new_thread(downloader.download, ())
            else:
                downloader.download()

def plobj(obj, otitle, cb, **kwargs): return obj(title = otitle, key = Callback(cb, **kwargs))
def dialog(title, message):           return ObjectContainer(header = title, message = message)
def confirm(otitle, ocb, **kwargs):   return plobj(PopupDirectoryObject, otitle, ocb, **kwargs)
def warning(otitle, ohandle, ocb, **kwargs):
    container = ObjectContainer(header = otitle)
    container.add(plobj(DirectoryObject, ohandle, ocb, **kwargs))

    return container

def plex_refresh_section(section):
    base    = 'http://127.0.0.1:32400/library/sections'
    query   = '//Directory[@type="%s"]' % section
    element = XML.ElementFromURL(base).xpath(query)[0]
    key     = element.get('key')
    url     = base + '/%s/refresh' % key

    HTTP.Request(url, immediate = True)
