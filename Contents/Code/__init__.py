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

SS_URL_SOURCES   = 'http://h.709scene.com/ss/sources?url=%s'
SS_URL_TRANSLATE = 'http://h.709scene.com/ss/translate?original=%s&foreign=%s'
SS_URL_WIZARD    = 'http://h.709scene.com/ss/wizard?url=%s'

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
        DirectoryObject(key = Callback(IcefilmsMenu), title = L('Icefilms')),
        DirectoryObject(key = Callback(WSOMenu),      title = L('Watchseries'))
    ])

    return container

@route(PLUGIN_PREFIX_ICEFILMS)
def IcefilmsMenu():
    container = ObjectContainer(objects = [
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
    return icefilms_container_permalinks(ICEFILMS_URL_LATEST)

@route('%s/tv' % PLUGIN_PREFIX_ICEFILMS)
def IcefilmsTV():
    """docstring for IcefilmsTV"""
    return ObjectContainer(objects = [
        DirectoryObject(key = Callback(IcefilmsTVAZ), title = L('by_letter')),
        DirectoryObject(key = Callback(IcefilmsTVByFilter, scope = 'popular'), title = L('by_popularity')),
        DirectoryObject(key = Callback(IcefilmsTVByFilter, scope = 'rating'),  title = L('by_rating')),
        DirectoryObject(key = Callback(IcefilmsTVByFilter, scope = 'release'), title = L('by_release'))
    ])

@route("%s/tv/a-z" % PLUGIN_PREFIX_ICEFILMS)
def IcefilmsTVAZ():
    """docstring for IcefilmsTVAZ"""

    return az_container(IcefilmsTVByLetter)

@route("%s/tv/a-z/{letter}" % PLUGIN_PREFIX_ICEFILMS)
def IcefilmsTVByLetter(letter):
    """docstring for AZList"""

    return icefilms_container_episode_list(ICEFILMS_URL_TVAZ % letter.upper())

@route('%s/tv/{scope}' % PLUGIN_PREFIX_ICEFILMS)
def IcefilmsTVByFilter(scope):
    """docstring for IcefilmsTVByFilter"""

    return icefilms_container_episode_list(ICEFILMS_URL_TVFILTER % scope)

@route("%s/tv/show/{i}/{j}" % PLUGIN_PREFIX_ICEFILMS)
def IcefilmsEpisodeList(i, j):
    """docstring for IcefilmsEpisodeList"""

    return icefilms_container_permalinks(ICEFILMS_URL_TVEPISODES % (i, j))

@route('%s/movies' % PLUGIN_PREFIX_ICEFILMS)
def IcefilmsMovies():
    """docstring for IcefilmsMovies"""
    return ObjectContainer(objects = [
        DirectoryObject(key = Callback(IcefilmsMoviesAZ), title = L('by_letter')),
        DirectoryObject(key = Callback(IcefilmsMoviesByFilter, scope = 'popular'), title = L('by_popularity')),
        DirectoryObject(key = Callback(IcefilmsMoviesByFilter, scope = 'rating'),  title = L('by_rating')),
        DirectoryObject(key = Callback(IcefilmsMoviesByFilter, scope = 'release'), title = L('by_release'))
    ])

@route('%s/movies/a-z' % PLUGIN_PREFIX_ICEFILMS)
def IcefilmsMoviesAZ():
    """docstring for IcefilmsMoviesAZ"""

    return az_container(IcefilmsMoviesByLetter)

@route('%s/movies/a-z/{letter}' % PLUGIN_PREFIX_ICEFILMS)
def IcefilmsMoviesByLetter(letter):
    """docstring for IcefilmsMoviesByLetter"""

    return icefilms_container_permalinks(ICEFILMS_URL_MOVIESAZ % letter.upper())

@route('%s/movies/{scope}' % PLUGIN_PREFIX_ICEFILMS)
def IcefilmsMoviesByFilter(scope):
    """docstring for IcefilmsMoviesByFilter"""

    return icefilms_container_permalinks(ICEFILMS_URL_MOVIESFILTER % letter.upper())

@route(PLUGIN_PREFIX_WSO)
def WSOMenu():
    """docstring for WSOMenu"""
    container = ObjectContainer(objects = [
        DirectoryObject(key = Callback(WSOLatest, page = 1), title = L('latest_releases')),
        DirectoryObject(key = Callback(WSOTV),               title = L('tv')),
        DirectoryObject(key = Callback(WSOSearch),           title = L('search'))
    ])

    return container

@route('%s/latest/{page}' % PLUGIN_PREFIX_WSO)
def WSOLatest(page = 1):
    """docstring for WSOLatest"""

    return wso_container_permalinks(WSO_URL_LATEST % page, page)

@route('%s/tv' % PLUGIN_PREFIX_WSO)
def WSOTV():
    """docstring for WSOTV"""

    return ObjectContainer(objects = [
        DirectoryObject(key = Callback(WSOTVAZ), title = L('by_letter')),
    ])

@route('%s/tv/a-z' % PLUGIN_PREFIX_WSO)
def WSOTVAZ():
    """docstring for WSOTVAZ"""

    return az_container(WSOTVByLetter)

@route('%s/tv/a-z/{letter}' % PLUGIN_PREFIX_WSO)
def WSOTVByLetter(letter):
    """docstring for WSOTVByLetter"""
    if letter == '1':
        letter = "'"

    container   = ObjectContainer()
    az_page     = HTML.ElementFromURL(WSO_URL_TVAZ)
    letter_list = az_page.get_element_by_id('goto_%s' % letter.upper()).getnext()

    for tup in letter_list.iterlinks():
        show_title = tup[0].text
        slug       = tup[2].split('/')[-1]

        container.add(
            DirectoryObject(
                key   = Callback(WSOEpisodeList, slug = slug, page = 1),
                title = show_title
            )
        )

    return container

@route('%s/tv/show/{slug}/{page}' % PLUGIN_PREFIX_WSO)
def WSOEpisodeList(slug, page):
    """docstring for WSOEpisodeList"""
    return wso_container_permalinks(WSO_URL_TVEPISODES % (slug, page), page)

@route('%s/search' % PLUGIN_PREFIX_WSO)
def WSOSearch():
    """docstring for WSOSearch"""
    pass

def SSListSources(url):
    """docstring for SSListSources"""
    container   = ObjectContainer()
    sources_url = SS_URL_SOURCES % String.Quote(url)
    sources     = JSON.ObjectFromURL(sources_url)

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

    video_object = VideoClipObject(url = actor_url, title = 'asdf')
    container.add(video_object)

    return container

def az_container(fn):
    """docstring for az_container"""
    container  = ObjectContainer()
    selections = list(string.uppercase)
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
            key   = Callback(SSListSources, url = ICEFILMS_URL_PERMALINK % item[0]),
            title = item[1]
        )
    )

    return container

def icefilms_container_episode_list(url):
    """docstring for icefilms_container_episode_list"""
    container  = ObjectContainer()

    for item in icefilmes_find_tvseries(url):
        container.add(DirectoryObject(key = Callback(IcefilmsEpisodeList, i = item[0], j = item[1]), title = item[2]))

    return container

def wso_container_permalinks(url, page):
    """docstring for wso_container_permalinks"""
    container     = ObjectContainer()
    next_page     = int(page) + 1
    list_page     = HTML.ElementFromURL(url)
    episode_links = list_page.cssselect('.content .Post a[rel="bookmark"]')

    for link in episode_links:
        container.add(DirectoryObject(
            key   = Callback(SSListSources, url = link.get('href')),
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
