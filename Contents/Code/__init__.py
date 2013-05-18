from ui import button, popup_button, input_button, dialog, confirm, warning

consts = SharedCodeService.consts
common = SharedCodeService.common

ss = common.init_ss()
import bridge_init
bridge = bridge_init.init_bridge()
slog = ss.util.getLogger('ss.plex')

def Start():
    # Initialize the plug-in
    Plugin.AddViewGroup('Details',  viewMode = 'InfoList',  mediaType = 'items')
    Plugin.AddViewGroup('List',     viewMode = 'List',      mediaType = 'items')

    ObjectContainer.view_group = 'List'
    ObjectContainer.art        = consts.art
    DirectoryObject.art        = consts.art
    slog.debug('"Starting" SS-Plex')

def ValidatePrefs(): pass

@handler(consts.prefix, consts.title, thumb = consts.icon, art = consts.art)
def MainMenu():
    container = generic.render_listings('/')

    container.add(button('heading.favorites',    favorites.MainMenu, icon = 'icon-favorites.png'))
    container.add(input_button('heading.search', 'search.prompt', SearchResultsMenu, icon = 'icon-search.png', foo = 1))
    container.add(button('search.heading.saved', search.MainMenu, icon = 'icon-saved-search.png'))
    container.add(button('heading.download',     downloads.MainMenu, refresh = 0, icon = 'icon-downloads.png'))
    container.add(button('heading.system',       system.MainMenu, icon = 'icon-system.png'))
    container.add(PrefsObject(title = L('system.heading.preferences')))

    return container

@route('%s/search/{query}')
def SearchResultsMenu(query, foo = 1):
    return search.ResultsMenu(query)

###################
# Listing Methods #
###################

@route('%s/ListSources' % consts.prefix)
def ListSources(endpoint, title):
    wizard = ss.Wizard(endpoint)
    return generic.render_listings_response(wizard.payload, endpoint, wizard.file_hint)

@route('%s/series/i{refresh}' % consts.prefix)
def ListTVShow(endpoint, show_title, refresh = 0):
    import re

    container, response = generic.render_listings(endpoint + '/episodes', show_title, return_response = True, flags = ['persisted'])
    title_regex         = r'^(. )?' + re.escape(show_title) + r':?\s+'

    for item in container.objects:
        item.title = re.sub(title_regex, '', str(item.title))

    labels   = [ 'add', 'remove' ]
    label    = labels[int(bridge.favorite.includes(endpoint))]

    container.objects.insert(0, button('favorites.heading.%s' % label, favorites.Toggle,
        endpoint   = endpoint,
        icon       = 'icon-favorites.png',
        show_title = show_title,
        overview   = (response or {}).get('resource', {}).get('display_overview'),
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
