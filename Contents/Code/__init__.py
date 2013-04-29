from ui import button, popup_button, input_button, dialog, confirm, warning

import ss
import bridge
import logging

consts = SharedCodeService.consts
slog   = logging.getLogger('ss.plex')

# TODO: remove once everything is extracted
#PLUGIN_PREFIX = consts.prefix
#PLUGIN_TITLE  = consts.title
#PLUGIN_ART    = consts.art
#PLUGIN_ICON   = consts.icon

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

###################
# Listing Methods #
###################

@route('%s/ListSources' % consts.prefix)
def ListSources(endpoint, title):
    wizard = Wizard(endpoint, environment = bridge.environment.plex)
    return render_listings_response(wizard.payload, endpoint, wizard.file_hint)

@route('%s/series/i{refresh}' % consts.prefix)
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
import favorites
import downloads
