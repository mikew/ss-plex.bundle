FEATURE_PREFIX = '%s/downloads' % consts.prefix

@route(FEATURE_PREFIX)
def MainMenu(refresh = 0):
    container = ObjectContainer(title1 = L('heading.download'))

    if bridge.download.assumed_running():
        download = bridge.download.current()
        endpoint = download['endpoint']
        status   = ss.downloader.status_for(endpoint, strategy = bridge.download.strategy())

        container.add(popup_button(download['title'], OptionsForCurrent,
            icon = 'icon-downloads.png'))

        for ln in status.report():
            container.add(popup_button('- %s' % ln, OptionsForCurrent,
                icon = 'icon-downloads.png'))

    for download in bridge.download.queue():
        container.add(popup_button(download['title'], OptionsForQueue,
            endpoint = download['endpoint'], icon = 'icon-downloads-queue.png'))

    for download in bridge.download.failed():
        container.add(popup_button(download['title'], OptionsForFailed,
            endpoint = download['endpoint'], icon = 'icon-downloads-failed.png'))

    add_refresh_to(container, refresh, MainMenu)
    return container

#@route('%s/show' % FEATURE_PREFIX)
#def Options(endpoint):
    #download = bridge.download.from_queue(endpoint)
    #failed   = bridge.download.from_failed(endpoint)

    #if download:
        #container     = ObjectContainer(title1 = download['title'])
        #cancel_button = button('download.heading.cancel', Cancel, endpoint = endpoint)

        #if bridge.download.is_current(endpoint):
            #if bridge.download.curl_running():
                #container.add(button('download.heading.next', NextSource))
                #container.add(cancel_button)
            #else:
                #container.add(button('download.heading.repair', DispatchForce))
        #else:
            #container.add(cancel_button)

        #return container
    #elif failed:
        #container     = ObjectContainer(title1 = failed['title'])
        #cancel_button = button('download.heading.cancel', RemoveFailed, endpoint = endpoint)
        #retry_button  = button('download.heading.retry', Queue,
            #endpoint   = failed['endpoint'],
            #media_hint = failed['media_hint'],
            #title      = failed['title'],
            #icon       = 'icon-downloads-queue.png'
        #)

        #container.add(retry_button)
        #container.add(cancel_button)

        #return container
    #else:
        #return dialog('heading.error', F('download.response.not-found', endpoint))

@route('%s/options-for-endpoint' % FEATURE_PREFIX)
def OptionsForEndpoint(endpoint):
    if bridge.download.is_current(endpoint):
        return OptionsForCurrent()

    queued = bridge.download.from_queue(endpoint)
    if queued: return OptionsForQueue(endpoint)

    failed = bridge.download.from_failed(endpoint)
    if failed: return OptionsForFailed(endpoint)

    return dialog('heading.error', F('download.response.not-found', endpoint))

@route('%s/options-for-current' % FEATURE_PREFIX)
def OptionsForCurrent():
    download  = bridge.download.current()
    container = ObjectContainer(title1 = download['title'])

    if bridge.download.curl_running():
        container.add(button('download.heading.next', NextSource))
        container.add(button('download.heading.cancel', RemoveCurrent))
    else:
        container.add(button('download.heading.repair', DispatchForce))

    return container

@route('%s/options-for-queue' % FEATURE_PREFIX)
def OptionsForQueue(endpoint):
    download = bridge.download.from_queue(endpoint)

    if download:
        container = ObjectContainer(title1 = download['title'])
        cancel_button = button('download.heading.cancel', Remove, endpoint = endpoint)
        container.add(cancel_button)

        return container
    else:
        return dialog('heading.error', F('download.response.not-found', endpoint))

@route('%s/options-for-failed' % FEATURE_PREFIX)
def OptionsForFailed(endpoint):
    download = bridge.download.from_failed(endpoint)

    if download:
        container     = ObjectContainer(title1 = download['title'])
        cancel_button = button('download.heading.cancel', RemoveFailed, endpoint = endpoint)
        retry_button  = button('download.heading.retry', Queue,
            endpoint   = download['endpoint'],
            media_hint = download['media_hint'],
            title      = download['title'],
            icon       = 'icon-downloads-queue.png'
        )

        container.add(retry_button)
        container.add(cancel_button)

        return container
    else:
        return dialog('heading.error', F('download.response.not-found', endpoint))

@route('%s/queue' % FEATURE_PREFIX)
def Queue(endpoint, media_hint, title):
    if bridge.download.includes(endpoint):
        message = 'exists'
    else:
        slog.info('Adding %s %s to download queue' % (media_hint, title))
        message = 'added'
        bridge.download.append(title = title, endpoint = endpoint, media_hint = media_hint)

    dispatch_download_threaded()
    return dialog('heading.download', F('download.response.%s' % message, title))

@route('%s/dispatch' % FEATURE_PREFIX)
def Dispatch():
    dispatch_download_threaded()

@route('%s/dispatch/force' % FEATURE_PREFIX)
def DispatchForce():
    slog.warning('Repairing downloads')
    bridge.download.clear_current()
    dispatch_download_threaded()

#@route('%s/cancel' % FEATURE_PREFIX)
#def Cancel(endpoint):
    #download = bridge.download.from_queue(endpoint)

    #if download:
        #if bridge.download.is_current(endpoint):
            #bridge.download.command('cancel')
        #else:
            #try:
                #slog.info('Removing %s from download queue' % endpoint)
                #bridge.download.remove(download)
            #except Exception, e:
                #slog.exception('Error cancelling download')
                #pass

        #return dialog('heading.download', F('download.response.cancel', download['title']))
    #else:
        #return dialog('heading.error', F('download.response.not-found', endpoint))

@route('%s/next' % FEATURE_PREFIX)
def NextSource():
    bridge.download.command('next')
    return dialog('heading.download', 'download.response.next')

@route('%s/remove' % FEATURE_PREFIX)
def Remove(endpoint):
    download = bridge.download.from_queue(endpoint)

    if not download:
        return dialog('heading.error',
                F('download.response.not-found', endpoint))

    bridge.download.remove(endpoint)
    return dialog('heading.download',
            F('download.response.cancel', download['title']))

@route('%s/remove-failed' % FEATURE_PREFIX)
def RemoveFailed(endpoint):
    download = bridge.download.from_failed(endpoint)

    if not download:
        return dialog('heading.error',
                F('download.response.not-found', endpoint))

    bridge.download.remove_failed(endpoint)
    return dialog('heading.download', 'download.response.remove-failed')

@route('%s/remove-current' % FEATURE_PREFIX)
def RemoveCurrent():
    download = bridge.download.current()
    bridge.download.command('cancel')

    return dialog('heading.download',
            F('download.response.cancel', download['title']))
