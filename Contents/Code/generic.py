def render_listings(endpoint, default_title = None, return_response = False, cache_time = None):
    slog.debug('Rendering listings for %s' % endpoint)
    listings_endpoint = util.listings_endpoint(endpoint)

    try:
        response  = JSON.ObjectFromURL(listings_endpoint, cacheTime = cache_time, timeout = 45)
        container = render_listings_response(response, endpoint = endpoint, default_title = default_title)
    except Exception, e:
        slog.exception('Error requesting %s' % endpoint)

        response  = None
        container = ObjectContainer(title1 = default_title)
        container.add(button('heading.error', noop))

    if return_response:
        return [ container, response ]
    else:
        return container

def render_listings_response(response, endpoint, default_title = None):
    container = ObjectContainer(
        title1 = response.get('title') or default_title,
        title2 = response.get('desc')
    )

    for element in response.get( 'items', [] ):
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

            if '/tv' == permalink:
                native.thumb = R('icon-tv.png')
            elif '/movies' == permalink :
                native.thumb = R('icon-movies.png')

        elif 'show' == element_type:
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

            native = PopupDirectoryObject(
                title   = display_title,
                tagline = tagline,
                thumb   = element.get('artwork'),
                summary = overview,
                key     = Callback(WatchOptions, endpoint = permalink, title = display_title, media_hint = media_hint)
            )

        elif 'foreign' == element_type:
            final_url = element.get('final_url')

            if final_url:
                service_url = '//ss/procedure?url=%s' % util.q(final_url)
            else:
                service_url = '//ss%s' % util.translate_endpoint(element['original_url'], element['foreign_url'], True)

            native = VideoClipObject(
                title = element['domain'],
                url   = '%s&endpoint=%s' % (service_url, util.q(endpoint))
            )

        #elif 'final' == element_type:
            #ss_url = '//ss/procedure?url=%s&title=%s' % (util.q(element['url']), util.q('FILE HINT HERE'))
            #native = VideoClipObject(url = ss_url, title = display_title)

        #elif 'movie' == element_type:
            #native = MovieObject(
                #rating_key = permalink,
                #title      = display_title,
                #tagline    = element.get( 'tagline' ),
                #summary    = element.get( 'desc' ),
                #key        = sources_callback
            #)
        #elif 'episode' == element_type:
            #native = EpisodeObject(
                #rating_key     = permalink,
                #title          = display_title,
                #summary        = element.get( 'desc' ),
                #season         = int( element.get( 'season', 0 ) ),
                #absolute_index = int( element.get( 'number', 0 ) ),
                #key            = sources_callback
            #)

        if None != native:
            container.add( native )

    return container
