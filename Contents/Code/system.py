@route('%s/system' % PLUGIN_PREFIX)
def SystemIndex():
    container = ObjectContainer(title1 = L('heading.system'))

    container.add(button('system.heading.reset',          SystemResetMenu, icon = 'icon-reset.png'))
    container.add(button('system.heading.status',         SystemStatus,    icon = 'icon-system-status.png'))
    container.add(button('system.heading.dispatch-force', DownloadsDispatchForce))

    return container

@route('%s/system/reset/menu' % PLUGIN_PREFIX)
def SystemResetMenu():
    container = ObjectContainer(title1 = L('system.heading.reset'))

    container.add(confirm('system.heading.reset-favorites',        SystemConfirmResetFavorites))
    container.add(confirm('system.heading.reset-search',           SystemConfirmResetSearches))
    container.add(confirm('system.heading.reset-download-history', SystemConfirmResetDownloads))
    container.add(confirm('system.heading.reset-download-failed',  SystemConfirmResetDownloadsFailed))
    container.add(confirm('system.heading.reset-ss-cache',         SystemConfirmResetSSCache))
    container.add(confirm('system.heading.reset-factory',          SystemConfirmResetFactory))

    return container

@route('%s/system/status' % PLUGIN_PREFIX)
def SystemStatus():
    container         = ObjectContainer(title1 = L('system.heading.status'))
    movie_destination = bridge.plex.section_destination('movie')
    show_destination  = bridge.plex.section_destination('show')
    download_strategy = bridge.download.strategy()

    container.add(button('Movies will be downloaded to %s'   % movie_destination,   noop))
    container.add(button('TV Shows will be downloaded to %s' % show_destination,    noop))
    container.add(button('Media will be downloaded with %s'  % download_strategy,   noop))
    container.add(button('version %s'                        % util.version.string, noop))

    return container

@route('%s/system/confirm/reset-favorites' % PLUGIN_PREFIX)
def SystemConfirmResetFavorites():
    return warning('system.warning.reset-favorites', 'confirm.yes', SystemResetFavorites)

@route('%s/system/confirm/reset-searches' % PLUGIN_PREFIX)
def SystemConfirmResetSearches():
    return warning('system.warning.reset-search', 'confirm.yes', SystemResetSearches)

@route('%s/system/confirm/reset-downloads' % PLUGIN_PREFIX)
def SystemConfirmResetDownloads():
    return warning('system.warning.reset-download-history', 'confirm.yes', SystemResetDownloads)

@route('%s/system/confirm/reset-downloads-failed' % PLUGIN_PREFIX)
def SystemConfirmResetDownloadsFailed():
    return warning('system.warning.reset-download-failed', 'confirm.yes', SystemResetDownloadsFailed)

@route('%s/system/confirm/reset-ss-cache' % PLUGIN_PREFIX)
def SystemConfirmResetSSCache():
    return warning('system.warning.reset-ss-cache', 'confirm.yes', SystemResetSSCache)

@route('%s/system/confirm/reset-factory' % PLUGIN_PREFIX)
def SystemConfirmResetFactory():
    return warning('system.warning.reset-factory', 'confirm.yes', SystemResetFactory)

@route('%s/system/reset/favorites' % PLUGIN_PREFIX)
def SystemResetFavorites():
    bridge.favorite.clear()
    return dialog('heading.system', 'system.response.reset-favorites')

@route('%s/system/reset/searches' % PLUGIN_PREFIX)
def SystemResetSearches():
    bridge.search.clear()
    return dialog('heading.system', 'system.response.reset-search')

@route('%s/system/reset/downloads' % PLUGIN_PREFIX)
def SystemResetDownloads():
    bridge.download.clear_history()
    return dialog('heading.system', 'system.response.reset-download-history')

@route('%s/system/reset/downloads-failed' % PLUGIN_PREFIX)
def SystemResetDownloadsFailed():
    bridge.download.clear_failed()
    return dialog('heading.system', 'system.response.reset-download-failed')

@route('%s/system/reset/ss-cache' % PLUGIN_PREFIX)
def SystemResetSSCache():
    util.clear_cache()
    return dialog('heading.system', 'system.response.reset-ss-cache')

@route('%s/system/reset/factory' % PLUGIN_PREFIX)
def SystemResetFactory():
    util.clear_cache()
    Dict.Reset()
    Dict.Save()
    return dialog('heading.system', 'system.response.reset-factory')
