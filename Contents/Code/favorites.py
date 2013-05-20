FEATURE_PREFIX = '%s/favorites' % consts.prefix

from generic import render_listings

@route(FEATURE_PREFIX)
def MainMenu():
    container = container_for('heading.favorites')

    if 'favorites' in Dict:
        container.add(button('favorites.heading.migrate', Migrate1to2))
    else:
        for endpoint, fav in ss.util.sorted_by_title(bridge.favorite.collection().iteritems(), lambda x: x[1]['title']):
            title  = fav['title']
            native = TVShowObject(
                rating_key = endpoint,
                title      = title,
                summary    = fav.get('overview'),
                thumb      = fav['artwork'],
                key        = Callback(ListTVShow, refresh = 0, endpoint = endpoint, show_title = title)
            )

            container.add(native)

    return container

@route('%s/toggle' % FEATURE_PREFIX)
def Toggle(endpoint, show_title, overview, artwork):
    message = None

    if bridge.favorite.includes(endpoint):
        slog.info('Removing %s from favorites' % show_title)
        message = 'favorites.response.removed'
        bridge.favorite.remove(endpoint)
    else:
        slog.info('Adding %s from favorites' % show_title)
        message = 'favorites.response.added'
        bridge.favorite.append(endpoint = endpoint,
                title = show_title,
                overview = overview,
                artwork = artwork)

    return dialog('heading.favorites', F(message, show_title))

@route('%s/migrate-1-2' % FEATURE_PREFIX)
def Migrate1to2():
    @thread
    def migrate():
        if 'favorites' in Dict:
            old_favorites = bridge.plex.user_dict()['favorites']
            new_favorites = bridge.favorite.collection()

            for endpoint, title in old_favorites.iteritems():
                if endpoint not in new_favorites:
                    try:
                        response = JSON.ObjectFromURL(ss.util.listings_endpoint(endpoint))
                        bridge.favorite.append(endpoint = endpoint, title = response['display_title'], artwork = response['artwork'])
                    except Exception, e:
                        #util.print_exception(e)
                        pass

            del Dict['favorites']
            bridge.plex.user_dict().Save()

    migrate()
    return dialog('Favorites', 'Your favorites are being updated. Return shortly.')
