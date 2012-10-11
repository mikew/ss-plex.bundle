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
    container     = render_listings(listings_endpoint('/'))
    favorite_item = DirectoryObject(
        title = 'Favorites',
        key   = Callback(Favorites)
    )

    container.add(favorite_item)
    return container

def has_dict(key):
    """docstring for has_dict"""
    if Dict[key]:
        return True
    else:
        return False

def show_is_favorite(show_title):
    """docstring for show_is_favorite"""
    return show_title in dict_default('favorites', {}).keys()

def dict_default(key, default = None):
    """docstring for dict_default"""
    if has_dict(key):
        return Dict[key]
    else:
        return default

def Favorites():
    """docstring for Favorites"""
    favorites = dict_default('favorites', {})
    container = ObjectContainer(
        title1 = 'Favorites'
    )

    for show_title, url in favorites.items():
        list_item = DirectoryObject(
            title = show_title,
            key   = Callback(ListTVShow, url = url, show_title = show_title)
        )

        container.add(list_item)

    return container

def RenderListings(url, default_title = None):
    """docstring for RenderListings"""
    return render_listings(url, default_title)

def ListTVShow(url, show_title):
    """docstring for ListTVShow"""
    container     = render_listings(url, show_title)
    if show_is_favorite(show_title):
        favorite_label = '- Remove from Favorites'
    else:
        favorite_label = '+ Add to Favorites'

    favorite_item = DirectoryObject(
        title = favorite_label,
        key   = Callback(ToggleFavorite, url = url, show_title = show_title)
    )

    container.objects.insert(0, favorite_item)
    return container

def ToggleFavorite(url, show_title):
    """docstring for AddFavorite"""
    if show_is_favorite(show_title):
        del Dict['favorites'][show_title]
    else:
        favorites             = dict_default('favorites', {})
        favorites[show_title] = url
        Dict['favorites']     = favorites

    #Dict['favorites'].save()

    return ListTVShow(url, show_title)

def ListSources(url, title):
    """docstring for SSListSources"""
    return render_listings(listings_endpoint('/sources?url=%s') % String.Quote(url), default_title = title)

def render_listings(url, default_title = None):
    """docstring for _render_listings"""
    Log('Attempting payload from %s' % (url))
    response  = JSON.ObjectFromURL(url)
    container = ObjectContainer(
        title1 = response.get( 'title' ) or default_title,
        title2 = response.get( 'desc' )
    )

    for element in response.get( 'items', [] ):
        naitive          = None
        permalink        = element.get('url')
        display_title    = element.get('display_title') or element.get('title')
        generic_callback = Callback(RenderListings, url = permalink, default_title = display_title)
        sources_callback = Callback(ListSources,    url = permalink, title         = display_title)

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
                key        = Callback(ListTVShow, url = permalink, show_title = display_title)
            )
        elif 'movie' == element['_type'] or 'episode' == element['_type']:
            Log('element is playable')
            naitive = DirectoryObject(
                title = display_title,
                key   = sources_callback
            )
        elif 'foreign' == element['_type']:
            Log('element is foreign')
            ss_url = '//ss/procedure?url=%s&title=%s' % (String.Quote(permalink), String.Quote('FILE HINT HERE'))
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
