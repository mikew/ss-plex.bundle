from datetime import datetime
import time
import re
import cgi

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
    #container = ObjectContainer()
    #index_page = HTML.StringFromElement(HTML.ElementFromURL('http://www.icefilms.info/'))
    #items = re.findall(r"<a href=\"/ip.php\?v=([\d]+)&amp;\">([^>]+)</a>", index_page)

    #for item in items:
        #container.add(
                #VideoClipObject(
                    #key = Callback(TranslateFinal, icefilms_id = item[0]),
                    #title = item[1]))

    container = MediaContainer(viewGroup="InfoList",title2=L('Episodes'))
    index_page = HTML.StringFromElement(HTML.ElementFromURL('http://www.icefilms.info/'))
    items = re.findall(r"<a href=\"/ip.php\?v=([\d]+)&amp;\">([^>]+)</a>", index_page)

    for item in items:
        container.Append(Function(VideoItem(TranslateFinal, title=item[1]), icefilms_id=item[0]))

    return container

def TranslateFinal(sender, icefilms_id):
    icefilms_url = "http://www.icefilms.info/ip.php?v=%s" % (icefilms_id)
    wizard_url   = "http://h.709scene.com/ss?v=%s" % (String.Quote(icefilms_url))
    json_data    = JSON.ObjectFromURL(wizard_url)
    final_url    = json_data['asset_url']
    return Redirect(final_url)

