consts = SharedCodeService.consts
common = SharedCodeService.common

from ui import (button, popup_button, input_button, dialog, confirm,
        warning, container_for, add_refresh_to, ensure_localized)
import plex_bridge
import updater

ss     = common.init_ss()
bridge = plex_bridge.init()
slog   = ss.util.getLogger('ss.plex')

updater.init(repo = 'mikew/ss-plex.bundle', branch = 'stable')

def Start():
    Plugin.AddViewGroup('Details', viewMode = 'InfoList', mediaType = 'items')
    Plugin.AddViewGroup('List',    viewMode = 'List',     mediaType = 'items')

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
    updater.add_button_to(container, PerformUpdate)
    return container

@route('%s/search/results/{query}' % consts.prefix)
def SearchResultsMenu(query, foo = 1):
    return search.ResultsMenu(query)

@route('%s/_update' % consts.prefix)
def PerformUpdate():
    return updater.PerformUpdate()

@route('%s/_noop' % consts.prefix)
def noop(): return dialog('hello', 'good day')

import generic
import system
import search
import favorites
import downloads
