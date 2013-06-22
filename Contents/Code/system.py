import downloads
import favorites
from generic import noop

FEATURE_PREFIX = '%s/system' % consts.prefix

@route(FEATURE_PREFIX)
def MainMenu():
    container = container_for('heading.system')

    container.add(button('system.heading.reset',          ResetMenu,  icon = 'icon-reset.png'))
    container.add(button('system.heading.status',         StatusMenu, icon = 'icon-system-status.png'))
    container.add(button('system.heading.dispatch-force', downloads.DispatchForce))
    container.add(button('system.heading.sync-favorites', favorites.Sync))

    return container

@route('%s/reset' % FEATURE_PREFIX)
def ResetMenu():
    container = container_for('system.heading.reset')

    container.add(confirm('system.heading.reset-favorites',        ConfirmResetFavorites))
    container.add(confirm('system.heading.reset-search',           ConfirmResetSearches))
    container.add(confirm('system.heading.reset-download-history', ConfirmResetDownloads))
    container.add(confirm('system.heading.reset-download-failed',  ConfirmResetDownloadsFailed))
    container.add(confirm('system.heading.reset-ss-cache',         ConfirmResetSSCache))
    container.add(confirm('system.heading.reset-factory',          ConfirmResetFactory))

    return container

@route('%s/status' % FEATURE_PREFIX)
def StatusMenu():
    container         = container_for('system.heading.status')
    movie_destination = bridge.settings.get('movie_destination')
    show_destination  = bridge.settings.get('show_destination')
    download_strategy = bridge.download.strategy()

    container.add(button(F('system.status.version',           consts.version), noop))
    container.add(button(F('system.status.movie-destination', movie_destination),   noop))
    container.add(button(F('system.status.show-destination',  show_destination),    noop))
    container.add(button(F('system.status.download-strategy', download_strategy),   noop))

    return container

@route('%s/confirm/reset-favorites' % FEATURE_PREFIX)
def ConfirmResetFavorites():
    return warning('system.warning.reset-favorites', 'confirm.yes', ResetFavorites)

@route('%s/confirm/reset-searches' % FEATURE_PREFIX)
def ConfirmResetSearches():
    return warning('system.warning.reset-search', 'confirm.yes', ResetSearches)

@route('%s/confirm/reset-downloads' % FEATURE_PREFIX)
def ConfirmResetDownloads():
    return warning('system.warning.reset-download-history', 'confirm.yes', ResetDownloads)

@route('%s/confirm/reset-downloads-failed' % FEATURE_PREFIX)
def ConfirmResetDownloadsFailed():
    return warning('system.warning.reset-download-failed', 'confirm.yes', ResetDownloadsFailed)

@route('%s/confirm/reset-ss-cache' % FEATURE_PREFIX)
def ConfirmResetSSCache():
    return warning('system.warning.reset-ss-cache', 'confirm.yes', ResetSSCache)

@route('%s/confirm/reset-factory' % FEATURE_PREFIX)
def ConfirmResetFactory():
    return warning('system.warning.reset-factory', 'confirm.yes', ResetFactory)

@route('%s/reset/favorites' % FEATURE_PREFIX)
def ResetFavorites():
    bridge.favorite.clear()
    return dialog('heading.system', 'system.response.reset-favorites')

@route('%s/reset/searches' % FEATURE_PREFIX)
def ResetSearches():
    bridge.search.clear()
    return dialog('heading.system', 'system.response.reset-search')

@route('%s/reset/downloads' % FEATURE_PREFIX)
def ResetDownloads():
    bridge.download.clear_history()
    return dialog('heading.system', 'system.response.reset-download-history')

@route('%s/reset/downloads-failed' % FEATURE_PREFIX)
def ResetDownloadsFailed():
    bridge.download.clear_failed()
    return dialog('heading.system', 'system.response.reset-download-failed')

@route('%s/reset/ss-cache' % FEATURE_PREFIX)
def ResetSSCache():
    ss.util.clear_cache()
    return dialog('heading.system', 'system.response.reset-ss-cache')

@route('%s/reset/factory' % FEATURE_PREFIX)
def ResetFactory():
    ss.util.clear_cache()
    Dict.Reset()
    Dict.Save()
    return dialog('heading.system', 'system.response.reset-factory')
