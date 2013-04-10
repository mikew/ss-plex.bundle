from ui import button, popup_button, input_button, dialog, confirm, warning

import ss
import bridge
import logging

consts = SharedCodeService.consts
slog   = logging.getLogger('ss.plex')

# TODO: remove once everything is extracted
PLUGIN_PREFIX = consts.prefix
PLUGIN_TITLE  = consts.title
PLUGIN_ART    = consts.art
PLUGIN_ICON   = consts.icon

to_export = dict(Log = Log, Dict = Dict, XML = XML, HTML = HTML, JSON = JSON, Prefs = Prefs, HTTP = HTTP, Platform = Platform)
bridge.plex.init(**to_export)

def Start():
    # Initialize the plug-in
    Plugin.AddViewGroup('Details',  viewMode = 'InfoList',  mediaType = 'items')
    Plugin.AddViewGroup('List',     viewMode = 'List',      mediaType = 'items')

    ObjectContainer.view_group = 'List'
    ObjectContainer.art        = R(PLUGIN_ART)
    DirectoryObject.art        = R(PLUGIN_ART)
    slog.debug('"Starting" SS-Plex')

def ValidatePrefs(): pass

@handler(consts.prefix, consts.title, thumb = consts.icon, art = consts.art)
def MainMenu():
    container = render_listings('/')

    container.add(button('heading.favorites',    FavoritesIndex, icon = 'icon-favorites.png'))
    container.add(input_button('heading.search', 'search.prompt', SearchResults, icon = 'icon-search.png', foo = 1))
    container.add(button('search.heading.saved', SearchIndex, icon = 'icon-saved-search.png'))
    container.add(button('heading.download',     DownloadsIndex, refresh = 0, icon = 'icon-downloads.png'))
    container.add(button('heading.system',       SystemIndex, icon = 'icon-system.png'))
    container.add(PrefsObject(title = L('system.heading.preferences')))

    return container

#############
# Favorites #
#############

@route('%s/favorites' % PLUGIN_PREFIX)
def FavoritesIndex():
    container = ObjectContainer(
        title1 = 'Favorites'
    )

    if 'favorites' in Dict:
        container.add(button('favorites.heading.migrate', FavoritesMigrate1to2))
    else:
        for endpoint, fav in util.sorted_by_title(bridge.favorite.collection().iteritems(), lambda x: x[1]['title']):
            title  = fav['title']
            native = TVShowObject(
                rating_key = endpoint,
                title      = title,
                thumb      = fav['artwork'],
                key        = Callback(ListTVShow, refresh = 0, endpoint = endpoint, show_title = title)
            )

            container.add(native)

    return container

@route('%s/favorites/toggle' % PLUGIN_PREFIX)
def FavoritesToggle(endpoint, show_title, artwork):
    message = None

    if bridge.favorite.includes(endpoint):
        slog.info('Removing %s from favorites' % show_title)
        message = 'favorites.response.removed'
        bridge.favorite.remove(endpoint)
    else:
        slog.info('Adding %s from favorites' % show_title)
        message = 'favorites.response.added'
        bridge.favorite.append(endpoint = endpoint, title = show_title, artwork = artwork)

    return dialog('heading.favorites', F(message, show_title))

def FavoritesMigrate1to2():
    @thread
    def migrate():
        if 'favorites' in Dict:
            old_favorites = bridge.plex.user_dict()['favorites']
            new_favorites = bridge.favorite.collection()

            for endpoint, title in old_favorites.iteritems():
                if endpoint not in new_favorites:
                    try:
                        response = JSON.ObjectFromURL(util.listings_endpoint(endpoint))
                        bridge.favorite.append(endpoint = endpoint, title = response['display_title'], artwork = response['artwork'])
                    except Exception, e:
                        #util.print_exception(e)
                        pass

            del Dict['favorites']
            bridge.plex.user_dict().Save()

    migrate()
    return dialog('Favorites', 'Your favorites are being updated. Return shortly.')

###############
# Downloading #
###############

@route('%s/downloads/i{refresh}' % PLUGIN_PREFIX)
def DownloadsIndex(refresh = 0):
    container = ObjectContainer(title1 = L('heading.download'))

    if bridge.download.assumed_running():
        current       = bridge.download.current()
        endpoint      = current['endpoint']
        status        = DownloadStatus(Downloader.status_file_for(endpoint), strategy = bridge.download.strategy())

        container.add(popup_button(current['title'], DownloadsOptions, endpoint = endpoint, icon = 'icon-downloads.png'))

        for ln in status.report():
            container.add(popup_button('- %s' % ln, DownloadsOptions, endpoint = endpoint, icon = 'icon-downloads.png'))

    for download in bridge.download.queue():
        container.add(popup_button(download['title'], DownloadsOptions, endpoint = download['endpoint'], icon = 'icon-downloads-queue.png'))

    for download in bridge.download.failed():
        container.add(popup_button(download['title'], DownloadsOptions, endpoint = download['endpoint'], icon = 'icon-downloads-failed.png'))

    add_refresh_to(container, refresh, DownloadsIndex)
    return container

@route('%s/downloads/show' % PLUGIN_PREFIX)
def DownloadsOptions(endpoint):
    download = bridge.download.from_queue(endpoint)
    failed   = bridge.download.from_failed(endpoint)

    if download:
        container     = ObjectContainer(title1 = download['title'])
        cancel_button = button('download.heading.cancel', DownloadsCancel, endpoint = endpoint)

        if bridge.download.is_current(endpoint):
            if bridge.download.curl_running():
                container.add(button('download.heading.next', DownloadsNext))
                container.add(cancel_button)
            else:
                container.add(button('download.heading.repair', DownloadsDispatchForce))
        else:
            container.add(cancel_button)

        return container
    elif failed:
        container     = ObjectContainer(title1 = failed['title'])
        cancel_button = button('download.heading.cancel', DownloadsRemoveFailed, endpoint = endpoint)
        retry_button  = button('download.heading.retry', DownloadsQueue,
            endpoint   = failed['endpoint'],
            media_hint = failed['media_hint'],
            title      = failed['title'],
            icon       = 'icon-downloads-queue.png'
        )

        container.add(retry_button)
        container.add(cancel_button)

        return container
    else:
        return dialog('heading.error', F('download.response.not-found', endpoint))

@route('%s/downloads/queue' % PLUGIN_PREFIX)
def DownloadsQueue(endpoint, media_hint, title):
    if bridge.download.in_history(endpoint):
        message = 'exists'
    else:
        slog.info('Adding %s %s to download queue' % (media_hint, title))
        message = 'added'
        bridge.download.append(title = title, endpoint = endpoint, media_hint = media_hint)

    dispatch_download_threaded()
    return dialog('heading.download', F('download.response.%s' % message, title))

@route('%s/downloads/dispatch' % PLUGIN_PREFIX)
def DownloadsDispatch():
    dispatch_download_threaded()

@route('%s/downloads/dispatch/force' % PLUGIN_PREFIX)
def DownloadsDispatchForce():
    slog.warning('Repairing downloads')
    bridge.download.clear_current()
    dispatch_download_threaded()

@route('%s/downloads/cancel' % PLUGIN_PREFIX)
def DownloadsCancel(endpoint):
    download = bridge.download.from_queue(endpoint)

    if download:
        if bridge.download.is_current(endpoint):
            bridge.download.command('cancel')
        else:
            try:
                slog.info('Removing %s from download queue' % endpoint)
                bridge.download.remove(download)
            except Exception, e:
                slog.exception('Error cancelling download')
                pass

        return dialog('heading.download', F('download.response.cancel', download['title']))
    else:
        return dialog('heading.error', F('download.response.not-found', endpoint))

@route('%s/downloads/next' % PLUGIN_PREFIX)
def DownloadsNext():
    bridge.download.command('next')
    return dialog('heading.download', 'download.response.next')

@route('%s/downloads/remove-failed' % PLUGIN_PREFIX)
def DownloadsRemoveFailed(endpoint):
    bridge.download.remove_failed(endpoint)
    return dialog('heading.download', 'download.response.remove-failed')

#########################
# Development Endpoints #
#########################

@route('%s/test' % PLUGIN_PREFIX)
def QuickTest():
    pass
    #import os
    #env = ""
    #for k, v in os.environ.iteritems():
        #env += "%s='%s' " % (k, v)

    #return dialog('test', env)

# UAS
@route('%s/update' % PLUGIN_PREFIX)
def UASUpdate():
    import uas
    return uas.updater.check(id = 'SS Plex', Dict = Dict, ObjectContainer = ObjectContainer)

###################
# Listing Methods #
###################

@route('%s/ListSources' % PLUGIN_PREFIX)
def ListSources(endpoint, title):
    wizard = Wizard(endpoint, environment = bridge.environment.plex)
    return render_listings_response(wizard.payload, endpoint, wizard.file_hint)

@route('%s/series/i{refresh}' % PLUGIN_PREFIX)
def ListTVShow(endpoint, show_title, refresh = 0):
    import re

    container, response = render_listings(endpoint + '/episodes', show_title, True)
    title_regex         = r'^' + re.escape(show_title) + r':?\s+'

    for item in container.objects:
        item.title = re.sub(title_regex, '', str(item.title))

    labels   = [ 'add', 'remove' ]
    label    = labels[int(bridge.favorite.includes(endpoint))]

    container.objects.insert(0, button('favorites.heading.%s' % label, FavoritesToggle,
        endpoint   = endpoint,
        icon       = 'icon-favorites.png',
        show_title = show_title,
        artwork    = (response or {}).get('resource', {}).get('artwork')
    ))

    add_refresh_to(container, refresh, ListTVShow,
        endpoint   = endpoint,
        show_title = show_title,
    )

    return container

##################
# Plugin Helpers #
##################

def noop(): return dialog('hello', 'good day')

def dispatch_download_threaded():
    bridge.download.dispatch()

def add_refresh_to(container, refresh, ocb, **kwargs):
    refresh           = int(refresh)
    kwargs['refresh'] = refresh + 1
    kwargs['icon']    = 'icon-refresh.png'

    if 0 < refresh:
        container.replace_parent = True

    container.add(button('heading.refresh', ocb, **kwargs))

    return container

import generic
import system
import search
#import downloads
#import favorites
