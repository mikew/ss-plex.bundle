import re
import string

PLUGIN_PREFIX = '/video/ssp'
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
def IcefilmsMenu():
    container = ObjectContainer(objects = [
        DirectoryObject(key = Callback(IcefilmsLatest),  title = L('latest_releases')),
        DirectoryObject(key = Callback(IcefilmsTV),      title = L('tv')),
        DirectoryObject(key = Callback(IcefilmsMovies),  title = L('movies')),
        DirectoryObject(key = Callback(IcefilmsSearch),  title = L('search'))
    ])

    return container

@route('%s/icefilms/search' % PLUGIN_PREFIX)
def IcefilmsSearch():
    """docstring for IcefilmsSearch"""
    pass

@route('%s/icefilms/latest' % PLUGIN_PREFIX)
def IcefilmsLatest():
    """docstring for IcefilmsLatest"""
    container = ObjectContainer()

    for item in icefilms_find_permalinks(ICEFILMS_URL_LATEST):
        container.add(DirectoryObject(key = Callback(IcefilmsCrossFingers, icefilms_id = item[0]), title = item[1]))

    return container

@route('%s/icefilms/tv' % PLUGIN_PREFIX)
def IcefilmsTV():
    """docstring for IcefilmsTV"""
    return ObjectContainer(objects = [
        DirectoryObject(key = Callback(IcefilmsTVAZ), title = L('by_letter')),
        DirectoryObject(key = Callback(IcefilmsTVByFilter, scope = 'popular'), title = L('by_popularity')),
        DirectoryObject(key = Callback(IcefilmsTVByFilter, scope = 'rating'),  title = L('by_rating')),
        DirectoryObject(key = Callback(IcefilmsTVByFilter, scope = 'release'), title = L('by_release'))
    ])

@route("%s/icefilms/tv/a-z" % (PLUGIN_PREFIX))
def IcefilmsTVAZ():
    """docstring for IcefilmsTVAZ"""
    container  = ObjectContainer()

    for letter in az_list():
        container.add(DirectoryObject(key = Callback(IcefilmsTVByLetter, letter = letter), title = letter))

    return container

@route("%s/icefilms/tv/a-z/{letter}" % (PLUGIN_PREFIX))
def IcefilmsTVByLetter(letter):
    """docstring for AZList"""
    if letter == '#':
        letter = '1'

    letter_url = ICEFILMS_URL_TVAZ % letter.upper()
    container  = ObjectContainer()

    for item in icefilmes_find_tvseries(letter_url):
        container.add(DirectoryObject(key = Callback(IcefilmsEpisodeList, i = item[0], j = item[1]), title = item[2]))

    return container

@route('%s/icefilms/tv/{scope}' % PLUGIN_PREFIX)
def IcefilmsTVByFilter(scope):
    """docstring for IcefilmsTVByFilter"""
    filter_page = ICEFILMS_URL_TVFILTER % scope
    container   = ObjectContainer()

    for item in icefilmes_find_tvseries(filter_page):
        container.add(DirectoryObject(key = Callback(IcefilmsEpisodeList, i = item[0], j = item[1]), title = item[2]))

    return container

@route("%s/icefilms/tv/show/{i}/{j}" % (PLUGIN_PREFIX))
def IcefilmsEpisodeList(i, j):
    """docstring for IcefilmsEpisodeList"""
    list_url  = ICEFILMS_URL_TVEPISODES % (i, j)
    container = ObjectContainer()

    for item in icefilms_find_permalinks(list_url):
        container.add(DirectoryObject(key = Callback(IcefilmsCrossFingers, icefilms_id = item[0]), title = item[1]))

    return container

@route('%s/icefilms/movies' % PLUGIN_PREFIX)
def IcefilmsMovies():
    """docstring for IcefilmsMovies"""
    return ObjectContainer(objects = [
        DirectoryObject(key = Callback(IcefilmsMoviesAZ), title = L('by_letter')),
        DirectoryObject(key = Callback(IcefilmsMoviesByFilter, scope = 'popular'), title = L('by_popularity')),
        DirectoryObject(key = Callback(IcefilmsMoviesByFilter, scope = 'rating'),  title = L('by_rating')),
        DirectoryObject(key = Callback(IcefilmsMoviesByFilter, scope = 'release'), title = L('by_release'))
    ])

@route('%s/icefilms/movies/a-z' % PLUGIN_PREFIX)
def IcefilmsMoviesAZ():
    """docstring for IcefilmsMoviesAZ"""
    container = ObjectContainer()

    for letter in az_list():
        container.add(DirectoryObject(key = Callback(IcefilmsMoviesByLetter, letter = letter), title = letter))

    return container

@route('%s/icefilms/movies/a-z/{letter}' % (PLUGIN_PREFIX))
def IcefilmsMoviesByLetter(letter):
    """docstring for IcefilmsMoviesByLetter"""
    if letter == '#':
        letter = '1'

    letter_url = ICEFILMS_URL_MOVIESAZ % letter.upper()
    container  = ObjectContainer()

    for item in icefilms_find_permalinks(letter_url):
        container.add(DirectoryObject(key = Callback(IcefilmsCrossFingers, icefilms_id = item[0]), title = item[1]))

    return container

@route('%s/icefilms/movies/{scope}' % PLUGIN_PREFIX)
def IcefilmsMoviesByFilter(scope):
    """docstring for IcefilmsMoviesByFilter"""
    filter_page = ICEFILMS_URL_MOVIESFILTER % scope
    container   = ObjectContainer()

    for item in icefilms_find_permalinks(filter_page):
        container.add(DirectoryObject(key = Callback(IcefilmsCrossFingers, icefilms_id = item[0]), title = item[1]))

    return container

@route('%s/icefilms/cross_fingers/{icefilms_id}' % PLUGIN_PREFIX)
def IcefilmsCrossFingers(icefilms_id):
    """docstring for IcefilmsCrossFingers"""
    container = ObjectContainer()
    container.add(VideoClipObject(url = ICEFILMS_URL_PERMALINK % icefilms_id, title = 'cross fingers'))

    return container

def az_list():
    """docstring for az_list"""
    selections = list(string.uppercase)
    selections.append('#')

    return selections

def icefilmes_find_tvseries(haystack_url):
    """docstring for icefilmes_find_tvseries"""
    return re.findall(ICEFILMS_FINDER_TVSERIES, HTTP.Request(haystack_url).content)

def icefilms_find_permalinks(haystack_url):
    """docstring for icefilms_find_permalinks"""
    return re.findall(ICEFILMS_FINDER_PERMALINK, HTTP.Request(haystack_url).content)

