import re
import string

PLUGIN_PREFIX = '/video/ssp'
PLUGIN_TITLE  = L('title')
PLUGIN_ART    = 'art-default.jpg'
PLUGIN_ICON   = 'icon-default.png'

#URL_SS_LISTINGS = 'http://h.709scene.com/ss/listings'
URL_SS_LISTINGS = 'http://localhost:9292'

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
    return render_listings(listings_endpoint('/'))


def RenderListings(url):
    """docstring for RenderListings"""
    return render_listings(String.Unquote(url))

def ListSources(url, title):
    """docstring for SSListSources"""
    container        = render_listings(listings_endpoint('/sources?url=%s') % String.Quote(url))
    container.title1 = title

    return container

#def WatchLater(url):
    #"""docstring for SSWatchLater"""
    #container = ObjectContainer(header = 'Watch Later', message = 'Check on something else')
    #values    = { 'download[url]': url }

    #HTTP.Request(SS_URL_QUEUE, values, cacheTime = 0)

    #return container

def render_listings(url):
    """docstring for _render_listings"""
    Log('Attempting payload from %s' % (url))
    response  = JSON.ObjectFromURL(url)
    container = ObjectContainer(
        title1 = response.get( 'title' ),
        title2 = response.get( 'desc' )
    )

    for element in response.get( 'items', [] ):
        naitive    = None
        permalink  = element.get('url')
        quoted_url = permalink
        #quoted_url = String.Quote(permalink)
        display_title = element.get('display_title') or element.get('title')

        if 'endpoint' == element['_type']:
            Log('element is endpoint')
            naitive = DirectoryObject(
                title   = display_title,
                tagline = element.get( 'tagline' ),
                summary = element.get( 'desc' ),
                key     = Callback( RenderListings, url = quoted_url )
            )
        elif 'show' == element['_type']:
            Log('element is show')
            naitive = TVShowObject(
                rating_key = permalink,
                title      = display_title,
                summary    = element.get( 'desc' ),
                key        = Callback( RenderListings, url = quoted_url)
            )
        elif 'movie' == element['_type'] or 'episode' == element['_type']:
            Log('element is playable')
            naitive = DirectoryObject(
                title = display_title,
                key   = Callback( ListSources, url = quoted_url, title = display_title )
            )
        elif 'foreign' == element['_type']:
            naitive = VideoClipObject(url = permalink, title = display_title)

        #elif 'movie' == element['_type']:
            #Log('element is movie')
            #naitive = MovieObject(
                #rating_key = permalink,
                #title      = display_title,
                #tagline    = element.get( 'tagline' ),
                #summary    = element.get( 'desc' ),
                #key        = Callback( ListSources, url = quoted_url, title = display_title )
            #)
        #elif 'episode' == element['_type']:
            #Log('element is episode')
            #naitive = EpisodeObject(
                #rating_key     = permalink,
                #title          = display_title,
                #summary        = element.get( 'desc' ),
                #season         = int( element.get( 'season', 0 ) ),
                #absolute_index = int( element.get( 'number', 0 ) ),
                #key            = Callback( ListSources, url = quoted_url, title = display_title )
            #)

        if None != naitive:
            container.add( naitive )

    return container

def listings_endpoint(endpoint):
    """docstring for listings_endpoint"""
    return URL_SS_LISTINGS + endpoint
