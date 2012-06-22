import re
import string
import string

PLUGIN_PREFIX = "/video/wso"
PLUGIN_TITLE          = L('Title')
PLUGIN_ART           = 'art-default.jpg'
PLUGIN_ICON          = 'icon-default.png'

def Start():
    # Initialize the plug-in
    Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    # Setup the default attributes for the ObjectContainer
    ObjectContainer.title1 = PLUGIN_TITLE
    ObjectContainer.view_group = 'List'
    ObjectContainer.art = R(PLUGIN_ART)

    # Setup the default attributes for the other objects
    DirectoryObject.thumb = R(PLUGIN_ICON)
    DirectoryObject.art = R(PLUGIN_ART)
    VideoClipObject.thumb = R(PLUGIN_ICON)
    VideoClipObject.art = R(PLUGIN_ART)

@handler(PLUGIN_PREFIX, PLUGIN_TITLE)
def Menu():
    container = ObjectContainer(
            objects = [
                DirectoryObject(
                    key = Callback(LatestReleases),
                    title = 'Latest Releases'
                    ),
                DirectoryObject(
                    key = Callback(AZList),
                    title = 'A-Z List'
                    ),
                DirectoryObject(
                    key = Callback(Search),
                    title = 'Search'
                    )
                ]
            )
    return container

@route("%s/tv/a-z" % (PLUGIN_PREFIX))
def AZList():
    """docstring for AZList"""
    container = ObjectContainer()
    for letter in list(string.uppercase):
        container.add(
                DirectoryObject(
                    key = Callback(ShowsByLetter, letter = letter),
                    title = letter
                    ))

    return container

def Search():
    """docstring for Search"""
    pass

@route("%s/latest" % (PLUGIN_PREFIX))
def LatestReleases():
    """docstring for LatestReleases"""
    container = ObjectContainer()
    index_page = HTML.StringFromElement(HTML.ElementFromURL('http://www.icefilms.info/'))
    items = re.findall(r"<a href=\"/ip.php\?v=([\d]+)&amp;\">([^>]+)</a>", index_page)

    for item in items:
        container.add(
                VideoClipObject(url = "http://www.icefilms.info/ip.php?v=%s" %
                    item[0], title = item[1])
                )
                #DirectoryObject(
                    #key = Callback(TranslateFinal, icefilms_id = item[0]),
                    #title = item[1]))

    return container

@route("%s/tv/a-z/{letter}" % (PLUGIN_PREFIX))
def ShowsByLetter(letter):
    """docstring for AZList"""
    letter_url = "http://www.icefilms.info/tv/a-z/%s" % (letter.upper())
    haystack = HTML.StringFromElement(HTML.ElementFromURL(letter_url))
    items = re.findall(r"<a href=\"/tv/series/(\d+)/(\d+)\">([^<]+)</a>", haystack)

    container = ObjectContainer()
    for item in items:
        container.add(
                DirectoryObject(
                    key   = Callback(EpisodeList, i=item[0], j=item[1]),
                    title = item[2]
                    ))

    return container

@route("%s/tv/show/{i}/{j}" % (PLUGIN_PREFIX))
def EpisodeList(i, j):
    """docstring for Episo"""
    list_url = "http://www.icefilms.info/tv/series/%s/%s" % (i, j)
    haystack = HTML.StringFromElement(HTML.ElementFromURL(list_url))
    items = re.findall(r"<a href=\"/ip.php\?v=([\d]+)&amp;\">([^>]+)</a>",
            haystack)

    container = ObjectContainer()
    for item in items:
        container.add(
                VideoClipObject(url="http://www.icefilms.info/ip.php?v=%s" %
                    item[0], title = item[1]))

    return container

#@route("%s/translate/{icefilms_id}" % PLUGIN_PREFIX)
