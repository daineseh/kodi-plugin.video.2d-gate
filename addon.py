#-*- coding: utf-8 -*-
import sys
import urllib
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import youtube_dl

from clawler import ParserAnimeFrom2dGate, ProcessEpisodes


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def page_number(url):
    return url.split('-')[-1].split('.')[0]

mode = args.get('mode', None)

if mode is None:
    obj = ParserAnimeFrom2dGate()
    for item in obj.get_classes():
        url = build_url({'mode': 'week_folder', 'folder_name': item})
        li = xbmcgui.ListItem(item, iconImage='DefaultFolder.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)

    target_url = obj.get_target_url()
    url = build_url({'mode': 'page', 'folder_name': target_url})
    li = xbmcgui.ListItem("[COLOR aqua]下一頁 (%s) >>[/COLOR]" % page_number(target_url))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'week_folder':
    obj = ParserAnimeFrom2dGate()
    folder_name = args['folder_name'][0]

    for anime_name in obj.get_content(folder_name):
        thumbnail = obj.get_thumb(folder_name, anime_name)
        url = build_url({'mode': 'anime_info', 'folder_name': obj.get_url(folder_name, anime_name)})
        li = xbmcgui.ListItem(anime_name)
        li.setArt({'thumb': thumbnail, 'icon': thumbnail, 'fanart': thumbnail})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'page':
    obj = ParserAnimeFrom2dGate()
    page_name = args['folder_name'][0]

    for anime in obj.get_page(page_name):
        url = build_url({'mode': 'anime_info', 'folder_name': anime.url})
        li = xbmcgui.ListItem(anime.name)
        li.setArt({'thumb': anime.thumb, 'icon': anime.thumb, 'fanart': anime.thumb})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    if obj.next_page:
        url = build_url({'mode': 'page', 'folder_name': obj.next_page})
        li = xbmcgui.ListItem("[COLOR aqua]下一頁 (%s) >>[/COLOR]" % page_number(obj.next_page))
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    if obj.last_page:
        url = build_url({'mode': 'page', 'folder_name': obj.last_page})
        li = xbmcgui.ListItem("[COLOR deepskyblue]最終頁 (%s) >|[/COLOR]" % page_number(obj.last_page))
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'anime_info':
    anime_url = args['folder_name'][0]
    ep = ProcessEpisodes(anime_url)

    for episode in ep.get_list():
        url = build_url({'mode': 'play', 'folder_name': episode.url})
        li = xbmcgui.ListItem(episode.name)
        li.setArt({'thumb': episode.thumb, 'icon': episode.thumb, 'fanart': episode.background})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'play':
    url = args['folder_name'][0]
    opts = {
        'forceurl': True,
        'quiet': True,
        'simulate': True,
    }

    with youtube_dl.YoutubeDL(opts) as ydl:
        resource_uri = ydl.extract_info(url).get('url')
        if not resource_uri:
            entries = ydl.extract_info(url).get('entries')
            resource_uri = entries[-1].get('url')
    xbmc.Player().play(resource_uri)

