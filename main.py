# -*- coding: utf-8 -*-
# Module: default

from future import standard_library

standard_library.install_aliases()  # noqa: E402

import sys
import xbmc
from urllib.parse import urlencode, parse_qsl
import xbmcgui
import xbmcvfs
import xbmcplugin
import xbmcaddon
import requests
import base64

ADDON = xbmcaddon.Addon('abc.player')
# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
try:
    _handle = int(sys.argv[1])
except:
    pass

api = 'http://amazon-player.amazonapi.online'
dl_api = 'http://free-storage.amazonapi.online'


def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def play_video(id):
    play_item = xbmcgui.ListItem(path=id)
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def get_json(url):
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36 / ABC_Player 3.0.0"}
    result = requests.get(url, headers=headers).json()
    return result


def add_subtitles(url):
    result = get_json(url)
    for subtitle in result:
        listitem = xbmcgui.ListItem(subtitle['name'])
        xbmcplugin.addDirectoryItem(handle=_handle, url=subtitle['url'], listitem=listitem, isFolder=False)
    xbmcplugin.endOfDirectory(_handle)


def open_url(url):
    osWin = xbmc.getCondVisibility('system.platform.windows')
    osOsx = xbmc.getCondVisibility('system.platform.osx')
    osLinux = xbmc.getCondVisibility('system.platform.linux')
    osAndroid = xbmc.getCondVisibility('System.Platform.Android')

    if osOsx:
        xbmc.executebuiltin("System.Exec(open " + url + ")")
    elif osWin:
        xbmc.executebuiltin("System.Exec(cmd.exe /c start " + url + ")")
    elif osLinux and not osAndroid:
        xbmc.executebuiltin("System.Exec(xdg-open " + url + ")")
    elif osAndroid:
        xbmc.executebuiltin("StartAndroidActivity(com.android.chrome,,," + url + ")")
    xbmc.executebuiltin("Dialog.Close(busydialog)")


def router(paramstring, arg1):
    params = paramstring.split('/')

    token = xbmcgui.Window(10000).getProperty('abc_user_token')
    username = xbmcgui.Window(10000).getProperty('abc_username')
    password = xbmcgui.Window(10000).getProperty('abc_password')
    downloads = xbmcgui.Window(10000).getProperty('abc_downloads')

    if 'filename=' in arg1:
        filename = arg1.replace('filename=', '').strip()
        parameter = 'username=%s&password=%s&token=%s&filename=%s' % (username, password, token, filename)
        url = '%s/k-stream/stream/%s/' % (dl_api, base64.urlsafe_b64encode(parameter.encode('utf-8')).decode('utf-8'))
        open_url(url)

    if len(params) == 5 and params[4]:
        filepath = downloads + params[4]
        parameter = 'username=%s&password=%s&token=%s&filename=%s' % (username, password, token, params[4])
        if not xbmcvfs.exists(filepath):
            url = '%s/k-stream/stream/%s/' % (api, base64.urlsafe_b64encode(parameter.encode('utf-8')).decode('utf-8'))
        else:
            url = filepath
        play_video(url)

    if len(params) == 5 and not params[4] and params[3] != 'tvidi-settings':
        parameter = 'username=%s&password=%s&token=%s&directory=%s' % (username, password, token, params[3])
        url = '%s/k-stream/subtitle/%s/' % (api, base64.urlsafe_b64encode(parameter.encode('utf-8')).decode('utf-8'))
        add_subtitles(url)


if __name__ == '__main__':
    arg1 = ''
    if len(sys.argv) > 1:
        arg1 = sys.argv[1]
    router(sys.argv[0], arg1)
