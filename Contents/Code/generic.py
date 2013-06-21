import downloads

@route('%s/RenderListings' % consts.prefix)
def RenderListings(endpoint, default_title = None):
    return render_listings(endpoint, default_title)

@route('%s/WatchOptions' % consts.prefix)
def WatchOptions(endpoint, title, media_hint):
    container    = render_listings(endpoint, default_title = title, cache_time = ss.cache.TIME_DAY)
    wizard_url   = '//ss/wizard?endpoint=%s&avoid_flv=%s&start_at=%s' % (
            endpoint, int(bridge.settings.get('avoid_flv_streaming', False)), 0)
    wizard_item  = VideoClipObject(title = L('media.watch-now'), url = wizard_url, thumb = R('icon-watch-now.png'))
    sources_item = button('media.all-sources', ListSources, endpoint = endpoint, title = title, icon = 'icon-view-all-sources.png')

    if bridge.download.includes(endpoint):
        download_item = button('media.persisted', downloads.OptionsForEndpoint, endpoint = endpoint, icon = 'icon-downloads-queue.png')
    else:
        download_item = button('media.watch-later', downloads.Queue,
            endpoint   = endpoint,
            media_hint = media_hint,
            title      = title,
            icon       = 'icon-downloads-queue.png'
        )

    container.objects.insert(0, wizard_item)
    container.objects.insert(1, download_item)
    container.objects.insert(2, sources_item)

    return container

def flag_title(title, endpoint, flags = None):
    flags = flags or ['persisted', 'favorite']

    if 'persisted' in flags and bridge.download.includes(endpoint):
        return F('generic.flag-persisted', title)

    if 'favorite' in flags and bridge.favorite.includes(endpoint):
        return F('generic.flag-favorite', title)

    return title

def render_listings(endpoint, default_title = None, return_response = False,
        cache_time = 120, flags = None):

    slog.debug('Rendering listings for %s' % endpoint)
    listings_endpoint = ss.util.listings_endpoint(endpoint)

    try:
        response  = JSON.ObjectFromURL(listings_endpoint, cacheTime = cache_time,
                timeout = 45)
        container = render_listings_response(response, endpoint = endpoint,
                default_title = default_title, flags = flags)
    except Exception, e:
        slog.exception('Error requesting %s' % endpoint)

        response  = None
        container = container_for(default_title)
        container.add(button('heading.error', noop))

    if return_response:
        return [ container, response ]
    else:
        return container

def render_listings_response(response, endpoint, default_title = None,
        flags = None):
    display_title = response.get('title') or default_title
    container = container_for(display_title)
    items = response.get('items', [])

    for i, element in enumerate(items):
        native           = None
        permalink        = element.get('endpoint')
        display_title    = element.get('display_title')    or element.get('title')
        overview         = element.get('display_overview') or element.get('overview')
        tagline          = element.get('display_tagline')  or element.get('tagline')
        element_type     = element.get('_type')
        generic_callback = Callback(RenderListings, endpoint = permalink, default_title = display_title)

        if 'endpoint' == element_type:
            native = DirectoryObject(
                title   = display_title,
                tagline = tagline,
                summary = overview,
                key     = generic_callback,
                thumb   = element.get('artwork')
            )

            if '/shows' == permalink:
                native.thumb = R('icon-tv.png')
            elif '/movies' == permalink:
                native.thumb = R('icon-movies.png')

        elif 'show' == element_type:
            if bridge.download.in_history(permalink):
                display_title = F('generic.in-history', display_title)

            native = TVShowObject(
                rating_key = permalink,
                title      = display_title,
                summary    = overview,
                thumb      = element.get('artwork'),
                key        = Callback(ListTVShow, refresh = 0, endpoint = permalink, show_title = display_title)
            )

        elif 'movie' == element_type or 'episode' == element_type:
            media_hint = element_type
            if 'episode' == media_hint:
                media_hint = 'show'

            display_title = flag_title(display_title, permalink, flags = flags)
            #display_title = str(display_title).encode('iso-8859-1').decode('utf-8')
            display_title = str(display_title).decode('utf-8')

            native = PopupDirectoryObject(
                title   = display_title,
                tagline = tagline,
                thumb   = element.get('artwork'),
                summary = overview,
                key     = Callback(WatchOptions, endpoint = permalink, title = display_title, media_hint = media_hint)
            )

        elif 'foreign' == element_type:
            wizard_url = '//ss/wizard?endpoint=%s&avoid_flv=%s&start_at=%s' % (
                    endpoint, int(bridge.settings.get('avoid_flv_streaming', False)), i)

            native = VideoClipObject(
                title = element['domain'],
                url   = wizard_url
            )

        if None != native:
            container.add( native )

    return container
