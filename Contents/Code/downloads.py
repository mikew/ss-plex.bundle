FEATURE_PREFIX = '%s/downloads' % consts.prefix

@route(FEATURE_PREFIX)
def MainMenu(refresh = 0):
    container = ObjectContainer(title1 = L('heading.download'))

    if bridge.download.assumed_running():
        current  = bridge.download.current()
        endpoint = current['endpoint']
        status   = ss.DownloadStatus(ss.Downloader.status_file_for(endpoint), strategy = bridge.download.strategy())

        container.add(popup_button(current['title'], Options, endpoint = endpoint, icon = 'icon-downloads.png'))

        for ln in status.report():
            container.add(popup_button('- %s' % ln, Options, endpoint = endpoint, icon = 'icon-downloads.png'))

    for download in bridge.download.queue():
        container.add(popup_button(download['title'], Options, endpoint = download['endpoint'], icon = 'icon-downloads-queue.png'))

    for download in bridge.download.failed():
        container.add(popup_button(download['title'], Options, endpoint = download['endpoint'], icon = 'icon-downloads-failed.png'))

    add_refresh_to(container, refresh, MainMenu)
    return container

@route('%s/show' % FEATURE_PREFIX)
def Options(endpoint):
    download = bridge.download.from_queue(endpoint)
    failed   = bridge.download.from_failed(endpoint)

    if download:
        container     = ObjectContainer(title1 = download['title'])
        cancel_button = button('download.heading.cancel', Cancel, endpoint = endpoint)

        if bridge.download.is_current(endpoint):
            if bridge.download.curl_running():
                container.add(button('download.heading.next', NextSource))
                container.add(cancel_button)
            else:
                container.add(button('download.heading.repair', DispatchForce))
        else:
            container.add(cancel_button)

        return container
    elif failed:
        container     = ObjectContainer(title1 = failed['title'])
        cancel_button = button('download.heading.cancel', RemoveFailed, endpoint = endpoint)
        retry_button  = button('download.heading.retry', Queue,
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

@route('%s/queue' % FEATURE_PREFIX)
def Queue(endpoint, media_hint, title):
    if bridge.download.in_history(endpoint):
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

@route('%s/cancel' % FEATURE_PREFIX)
def Cancel(endpoint):
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

@route('%s/next' % FEATURE_PREFIX)
def NextSource():
    bridge.download.command('next')
    return dialog('heading.download', 'download.response.next')

@route('%s/remove-failed' % FEATURE_PREFIX)
def RemoveFailed(endpoint):
    bridge.download.remove_failed(endpoint)
    return dialog('heading.download', 'download.response.remove-failed')
