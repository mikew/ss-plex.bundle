import string
from consumer import listings_endpoint

PLUGIN_PREFIX = '/video/ssp'
PLUGIN_TITLE  = L('title')
PLUGIN_ART    = 'art-default.jpg'
PLUGIN_ICON   = 'icon-default.png'

def Start():
    # Initialize the plug-in
    Plugin.AddViewGroup("Details",  viewMode = "InfoList",  mediaType = "items")
    Plugin.AddViewGroup("List",     viewMode = "List",      mediaType = "items")

    # Setup the default attributes for the ObjectContainer
    ObjectContainer.title1     = PLUGIN_TITLE
    ObjectContainer.view_group = 'List'
    ObjectContainer.art        = R(PLUGIN_ART)

    # Setup the default attributes for the other objects
    DirectoryObject.thumb = R(PLUGIN_ICON)
    DirectoryObject.art   = R(PLUGIN_ART)
    VideoClipObject.thumb = R(PLUGIN_ICON)
    VideoClipObject.art   = R(PLUGIN_ART)

@handler(PLUGIN_PREFIX, PLUGIN_TITLE)
def MainMenu():
    """docstring for MainMenu"""
    container     = render_listings('/')

    favorite_item = DirectoryObject(
        title = 'Favorites',
        key   = Callback(Favorites)
    )

    search_item = InputDirectoryObject(
        key = Callback(SearchResults),
        title = 'Search',
        prompt = 'Search for ...'
    )

    saved_item = DirectoryObject(
        title = 'Saved Searches',
        key   = Callback(SavedSearches)
    )

    container.add(favorite_item)
    container.add(search_item)
    container.add(saved_item)

    return container

@route('%s/search' % PLUGIN_PREFIX)
def SearchResults(query):
    """docstring for SearchResults"""
    container = render_listings('/search/%s' % String.Quote(query))
    save_item = DirectoryObject(
        title = 'Save this search',
        key   = Callback(SaveSearch, query = query)
    )

    container.add(save_item)
    return container

@route('%s/searches' % PLUGIN_PREFIX)
def SavedSearches():
    """docstring for SavedSearches"""
    container = ObjectContainer()
    for query in sorted(dict_default('searches', [])):
        item = DirectoryObject(title = query, key = Callback(SearchResults, query = query))
        container.add(item)

    return container

@route('%s/save-search' % PLUGIN_PREFIX)
def SaveSearch(query):
    """docstring for SaveSearch"""
    saved_searches = dict_default('searches', [])

    if query not in saved_searches:
        saved_searches.append(query)

    Dict['searches'] = saved_searches

    return ObjectContainer(header = 'Saved', message = 'Your search has been saved.')

def has_dict(key):
    """docstring for has_dict"""
    if Dict[key]:
        return True
    else:
        return False

def show_is_favorite(endpoint):
    """docstring for show_is_favorite"""
    return endpoint in dict_default('favorites', {}).keys()

def dict_default(key, default = None):
    """docstring for dict_default"""
    if has_dict(key):
        return Dict[key]
    else:
        return default

@route('%s/favorites' % PLUGIN_PREFIX)
def Favorites():
    """docstring for Favorites"""
    favorites = dict_default('favorites', {})
    container = ObjectContainer(
        title1 = 'Favorites'
    )

    for endpoint, title in sorted(favorites.iteritems(), key = lambda x:x[1]):
        list_item  = DirectoryObject(
            title = title,
            key   = Callback(ListTVShow, endpoint = endpoint, show_title = title)
        )

        container.add(list_item)

    container.add(DirectoryObject(
        title = 'Clear Favorites',
        key   = Callback(ClearFavorites)
    ))

    return container

@route('%s/favorites/clear' % PLUGIN_PREFIX)
def ClearFavorites():
    """docstring for ClearFavorites"""
    Dict['favorites'] = {}
    return ObjectContainer(header = 'Favorites', message = 'Your favorites have been cleared.')

@route('%s/RenderListings' % PLUGIN_PREFIX)
def RenderListings(endpoint, default_title = None):
    """docstring for RenderListings"""
    return render_listings(endpoint, default_title)

@route('%s/series' % PLUGIN_PREFIX)
def ListTVShow(endpoint, show_title, refresh = 0):
    """docstring for ListTVShow"""
    container = render_listings(endpoint, show_title)
    if 0 < refresh:
        container.replace_parent = True

    if show_is_favorite(endpoint):
        favorite_label = '- Remove from Favorites'
    else:
        favorite_label = '+ Add to Favorites'

    favorite_item = DirectoryObject(
        title = favorite_label,
        key   = Callback(ToggleFavorite, endpoint = endpoint, show_title = show_title)
    )

    refresh_item = DirectoryObject(
        title = 'Refresh',
        key   = Callback(ListTVShow, endpoint = endpoint, show_title = show_title, refresh = refresh + 1)
    )

    container.objects.insert(0, favorite_item)
    container.add(refresh_item)

    return container

@route('%s/favorites/toggle' % PLUGIN_PREFIX)
def ToggleFavorite(endpoint, show_title):
    """docstring for AddFavorite"""
    message = None

    if show_is_favorite(endpoint):
        del Dict['favorites'][endpoint]
        message = '%s was removed from your favorites.'
    else:
        favorites             = dict_default('favorites', {})
        favorites[endpoint]   = show_title
        message               = '%s was added to your favorites.'
        Dict['favorites']     = favorites

    #Dict['favorites'].save()

    return ObjectContainer(header = 'Favorites', message = message % show_title)

def render_listings(endpoint, default_title = None):
    """docstring for _render_listings"""
    endpoint = listings_endpoint(endpoint)

    Log('Attempting payload from %s' % (endpoint))
    response  = JSON.ObjectFromURL(endpoint)
    container = ObjectContainer(
        title1 = response.get( 'title' ) or default_title,
        title2 = response.get( 'desc' )
    )

    for element in response.get( 'items', [] ):
        naitive          = None
        permalink        = element.get('endpoint')
        display_title    = element.get('display_title') or element.get('title')
        generic_callback = Callback(RenderListings, endpoint = permalink, default_title = display_title)

        if 'endpoint' == element['_type']:
            Log('element is endpoint')
            naitive = DirectoryObject(
                title   = display_title,
                tagline = element.get( 'tagline' ),
                summary = element.get( 'desc' ),
                key     = generic_callback
            )
        elif 'show' == element['_type']:
            Log('element is show')
            naitive = TVShowObject(
                rating_key = permalink,
                title      = display_title,
                summary    = element.get( 'desc' ),
                key        = Callback(ListTVShow, endpoint = permalink, show_title = display_title)
            )
        elif 'movie' == element['_type'] or 'episode' == element['_type']:
            Log('element is playable')
            naitive = DirectoryObject(
                title = display_title,
                key   = generic_callback
            )
        elif 'foreign' == element['_type']:
            Log('element is foreign')
            naitive = DirectoryObject(
                title = element['domain'],
                key   = generic_callback
            )
        elif 'final' == element['_type']:
            Log('element is final')
            ss_url = '//ss/procedure?url=%s&title=%s' % (String.Quote(element['url']), String.Quote('FILE HINT HERE'))
            naitive = VideoClipObject(url = ss_url, title = display_title)

        #elif 'movie' == element['_type']:
            #Log('element is movie')
            #naitive = MovieObject(
                #rating_key = permalink,
                #title      = display_title,
                #tagline    = element.get( 'tagline' ),
                #summary    = element.get( 'desc' ),
                #key        = sources_callback
            #)
        #elif 'episode' == element['_type']:
            #Log('element is episode')
            #naitive = EpisodeObject(
                #rating_key     = permalink,
                #title          = display_title,
                #summary        = element.get( 'desc' ),
                #season         = int( element.get( 'season', 0 ) ),
                #absolute_index = int( element.get( 'number', 0 ) ),
                #key            = sources_callback
            #)

        if None != naitive:
            container.add( naitive )

    return container
