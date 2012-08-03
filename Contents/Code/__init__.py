import re
import string

PLUGIN_PREFIX          = '/video/ssp'
PLUGIN_PREFIX_WSO      = '%s/wso'      % PLUGIN_PREFIX
PLUGIN_PREFIX_ICEFILMS = '%s/icefilms' % PLUGIN_PREFIX

PLUGIN_TITLE  = L('title')
PLUGIN_ART    = 'art-default.jpg'
PLUGIN_ICON   = 'icon-default.png'

ICEFILMS_URL_PERMALINK    = 'http://www.icefilms.info/ip.php?v=%s'
ICEFILMS_URL_TVAZ         = 'http://www.icefilms.info/tv/a-z/%s'
ICEFILMS_URL_TVFILTER     = 'http://www.icefilms.info/tv/%s/1'
ICEFILMS_URL_MOVIESAZ     = 'http://www.icefilms.info/movies/a-z/%s'
ICEFILMS_URL_MOVIESFILTER = 'http://www.icefilms.info/movies/%s/1'
ICEFILMS_URL_LATEST       = 'http://www.icefilms.info/'
ICEFILMS_URL_TVEPISODES   = 'http://www.icefilms.info/tv/series/%s/%s'
ICEFILMS_FINDER_PERMALINK = r"<a href=\"?/ip.php\?v=([\d]+)(?:&|&amp;)?\"?>([^>]+)</a>"
ICEFILMS_FINDER_TVSERIES  = r"<a href=\"?/tv/series/(\d+)/(\d+)\"?>([^<]+)</a>"

SS_URL_SOURCES   = 'http://h.709scene.com/ss/plex/sources?url=%s'
SS_URL_TRANSLATE = 'http://h.709scene.com/ss/plex/translate?original=%s&foreign=%s'
SS_URL_WIZARD    = 'http://h.709scene.com/ss/plex/wizard?url=%s'
SS_URL_QUEUE     = 'http://h.709scene.com/ss/downloads.json'

WSO_URL_LATEST     = 'http://www.watchseries-online.eu/page/%s'
WSO_URL_TVAZ       = 'http://www.watchseries-online.eu/2005/07/index.html'
WSO_URL_TVEPISODES = 'http://www.watchseries-online.eu/category/%s/page/%s'

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
    container = ObjectContainer(objects = [
        DirectoryObject(key = Callback(IcefilmsMenu), title = L('icefilms')),
        DirectoryObject(key = Callback(WSOMenu),      title = L('wso'))
    ])

    return container

@route(PLUGIN_PREFIX_ICEFILMS)
def IcefilmsMenu():
    container = ObjectContainer(title1 = L('icefilms'), objects = [
        DirectoryObject(key = Callback(IcefilmsLatest),  title = L('latest_releases')),
        DirectoryObject(key = Callback(IcefilmsTV),      title = L('tv')),
        DirectoryObject(key = Callback(IcefilmsMovies),  title = L('movies')),
        DirectoryObject(key = Callback(IcefilmsSearch),  title = L('search'))
    ])

    return container

@route('%s/search' % PLUGIN_PREFIX_ICEFILMS)
def IcefilmsSearch():
    """docstring for IcefilmsSearch"""
    pass

@route('%s/latest' % PLUGIN_PREFIX_ICEFILMS)
def IcefilmsLatest():
    """docstring for IcefilmsLatest"""
    container        = icefilms_container_permalinks(ICEFILMS_URL_LATEST)
    container.title1 = L('latest_releases')
    container.title2 = L('icefilms')

    return container

@route('%s/tv' % PLUGIN_PREFIX_ICEFILMS)
def IcefilmsTV():
    """docstring for IcefilmsTV"""
    return ObjectContainer(title1 = L('tv'), title2 = L('icefilms'), objects = [
        DirectoryObject(key = Callback(IcefilmsTVAZ), title = L('by_letter')),
        DirectoryObject(key = Callback(IcefilmsTVByFilter, scope = 'popular'), title = L('by_popularity')),
        DirectoryObject(key = Callback(IcefilmsTVByFilter, scope = 'rating'),  title = L('by_rating')),
        DirectoryObject(key = Callback(IcefilmsTVByFilter, scope = 'release'), title = L('by_release'))
    ])

@route("%s/tv/a-z" % PLUGIN_PREFIX_ICEFILMS)
def IcefilmsTVAZ():
    """docstring for IcefilmsTVAZ"""
    container        = az_container(IcefilmsTVByLetter)
    container.title2 = L('icefilms')

    return container

@route("%s/tv/a-z/{letter}" % PLUGIN_PREFIX_ICEFILMS)
def IcefilmsTVByLetter(letter):
    """docstring for IcefilmsTVByLetter"""
    container        = icefilms_container_episode_list(ICEFILMS_URL_TVAZ % letter.upper())
    container.title1 = F('tv_by_letter', letter.upper())
    container.title2 = L('icefilms')

    return container

@route('%s/tv/{scope}' % PLUGIN_PREFIX_ICEFILMS)
def IcefilmsTVByFilter(scope):
    """docstring for IcefilmsTVByFilter"""
    container        = icefilms_container_episode_list(ICEFILMS_URL_TVFILTER % scope)
    container.title1 = L('tv_by_%s' % scope)
    container.title2 = L('icefilms')

    return container

@route("%s/tv/show/{i}/{j}" % PLUGIN_PREFIX_ICEFILMS)
def IcefilmsEpisodeList(i, j, show):
    """docstring for IcefilmsEpisodeList"""
    container        = icefilms_container_permalinks(ICEFILMS_URL_TVEPISODES % (i, j))
    container.title1 = show
    container.title2 = L('icefilms')

    return container

@route('%s/movies' % PLUGIN_PREFIX_ICEFILMS)
def IcefilmsMovies():
    """docstring for IcefilmsMovies"""
    return ObjectContainer(title1 = L('movies'), title2 = L('icefilms'), objects = [
        DirectoryObject(key = Callback(IcefilmsMoviesAZ), title = L('by_letter')),
        DirectoryObject(key = Callback(IcefilmsMoviesByFilter, scope = 'popular'), title = L('by_popularity')),
        DirectoryObject(key = Callback(IcefilmsMoviesByFilter, scope = 'rating'),  title = L('by_rating')),
        DirectoryObject(key = Callback(IcefilmsMoviesByFilter, scope = 'release'), title = L('by_release'))
    ])

@route('%s/movies/a-z' % PLUGIN_PREFIX_ICEFILMS)
def IcefilmsMoviesAZ():
    """docstring for IcefilmsMoviesAZ"""
    container        = az_container(IcefilmsMoviesByLetter)
    container.title2 = L('icefilms')

    return container

@route('%s/movies/a-z/{letter}' % PLUGIN_PREFIX_ICEFILMS)
def IcefilmsMoviesByLetter(letter):
    """docstring for IcefilmsMoviesByLetter"""
    container        = icefilms_container_permalinks(ICEFILMS_URL_MOVIESAZ % letter.upper())
    container.title1 = F('movies_by_letter', letter.upper())
    container.title2 = L('icefilms')

    return container

@route('%s/movies/{scope}' % PLUGIN_PREFIX_ICEFILMS)
def IcefilmsMoviesByFilter(scope):
    """docstring for IcefilmsMoviesByFilter"""
    container        = icefilms_container_permalinks(ICEFILMS_URL_MOVIESFILTER % scope)
    container.title1 = L('movies_by_%s' % scope)
    container.title2 = L('icefilms')

    return container

@route(PLUGIN_PREFIX_WSO)
def WSOMenu():
    """docstring for WSOMenu"""
    container = ObjectContainer(title1 = L('wso'), objects = [
        DirectoryObject(key = Callback(WSOLatest, page = 1), title = L('latest_releases')),
        DirectoryObject(key = Callback(WSOTV),               title = L('tv')),
        DirectoryObject(key = Callback(WSOSearch),           title = L('search'))
    ])

    return container

@route('%s/latest/{page}' % PLUGIN_PREFIX_WSO)
def WSOLatest(page = 1):
    """docstring for WSOLatest"""
    container        = wso_container_permalinks(WSO_URL_LATEST % page, page)
    container.title1 = L('latest_releases')
    container.title2 = L('wso')

    return container

@route('%s/tv' % PLUGIN_PREFIX_WSO)
def WSOTV():
    """docstring for WSOTV"""

    return ObjectContainer(title1 = L('tv'), title2 = L('wso'), objects = [
        DirectoryObject(key = Callback(WSOTVAZ), title = L('by_letter')),
    ])

@route('%s/tv/a-z' % PLUGIN_PREFIX_WSO)
def WSOTVAZ():
    """docstring for WSOTVAZ"""
    container        = az_container(WSOTVByLetter)
    container.title2 = L('wso')

    return container

@route('%s/tv/a-z/{letter}' % PLUGIN_PREFIX_WSO)
def WSOTVByLetter(letter):
    """docstring for WSOTVByLetter"""
    if letter == '1':
        letter = "'"

    container   = ObjectContainer(title1 = F('tv_by_letter', letter.upper()), title2 = L('wso'))
    az_page     = HTML.ElementFromURL(WSO_URL_TVAZ)
    letter_list = az_page.get_element_by_id('goto_%s' % letter.upper()).getnext()

    for tup in letter_list.iterlinks():
        show_title = tup[0].text
        slug       = tup[2].split('/')[-1]

        container.add(
            DirectoryObject(
                key   = Callback(WSOEpisodeList, slug = slug, page = 1, show = show_title),
                title = show_title
            )
        )

    return container

@route('%s/tv/show/{slug}/{page}' % PLUGIN_PREFIX_WSO)
def WSOEpisodeList(slug, page, show):
    """docstring for WSOEpisodeList"""
    container        = wso_container_permalinks(WSO_URL_TVEPISODES % (slug, page), page)
    container.title1 = show
    container.title2 = L('wso')

    return container

@route('%s/search' % PLUGIN_PREFIX_WSO)
def WSOSearch():
    """docstring for WSOSearch"""
    pass

def SSListSources(url, title):
    """docstring for SSListSources"""
    container   = ObjectContainer(title1 = title)
    sources_url = SS_URL_SOURCES % String.Quote(url)
    sources     = JSON.ObjectFromURL(sources_url)

    container.add(DirectoryObject(
        key   = Callback(SSWatchLater, url = url),
        title = L('watch_later')
    ))

    for pair in sources:
        foreign      = pair[0]
        source_hint  = pair[1]
        source_title = 'Watch on %s' % source_hint

        container.add(
            DirectoryObject(
                key   = Callback(SSTranslateFinal, original = url, foreign = foreign),
                title = source_title
            )
        )

    return container

def SSTranslateFinal(original, foreign):
    """docstring for TranslateFinal"""
    container     = ObjectContainer()
    translate_url = SS_URL_TRANSLATE % (String.Quote(original), String.Quote(foreign))
    actor_url     = JSON.ObjectFromURL(translate_url)

    video_object = VideoClipObject(url = actor_url['url'], title = 'asdf')
    container.add(video_object)

    return container

def SSWatchLater(url):
    """docstring for SSWatchLater"""
    container = ObjectContainer(header = 'Watch Later', message = 'Check on something else')
    values    = { 'download[url]': url }

    HTTP.Request(SS_URL_QUEUE, values, cacheTime = 0)

    return container

def az_container(fn):
    """docstring for az_container"""
    container        = ObjectContainer()
    container.title1 = L('pick_letter')
    selections       = list(string.uppercase)
    selections.append('1')

    for letter in selections:
        container.add(DirectoryObject(key = Callback(fn, letter = letter), title = letter))

    return container

def icefilmes_find_tvseries(haystack_url):
    """docstring for icefilmes_find_tvseries"""
    return re.findall(ICEFILMS_FINDER_TVSERIES, HTTP.Request(haystack_url).content)

def icefilms_find_permalinks(haystack_url):
    """docstring for icefilms_find_permalinks"""
    return re.findall(ICEFILMS_FINDER_PERMALINK, HTTP.Request(haystack_url).content)

def icefilms_container_permalinks(url):
    """docstring for icefilms_container_permalinks"""
    container = ObjectContainer()

    for item in icefilms_find_permalinks(url):
        container.add(DirectoryObject(
            key   = Callback(SSListSources, url = ICEFILMS_URL_PERMALINK % item[0], title = item[1]),
            title = item[1]
        )
    )

    return container

def icefilms_container_episode_list(url):
    """docstring for icefilms_container_episode_list"""
    container  = ObjectContainer()

    for item in icefilmes_find_tvseries(url):
        container.add(DirectoryObject(
            title = item[2],
            key   = Callback(IcefilmsEpisodeList,
                i    = item[0],
                j    = item[1],
                show = item[2]
            )
        ))

    return container

def wso_container_permalinks(url, page):
    """docstring for wso_container_permalinks"""
    container     = ObjectContainer()
    next_page     = int(page) + 1
    list_page     = HTML.ElementFromURL(url)
    episode_links = list_page.cssselect('.content .Post a[rel="bookmark"]')

    for link in episode_links:
        container.add(DirectoryObject(
            key   = Callback(SSListSources, url = link.get('href'), title = link.text.strip()),
            title = link.text.strip()
        )
    )

    container.add(
        DirectoryObject(
            key   = Callback(WSOLatest, page = next_page),
            title = 'Page %s' % next_page
        )
    )

    return container
