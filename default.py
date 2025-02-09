import xbmc
import xbmcgui
import xbmcplugin
import os
import sys
import requests
import json

# Plugin constants
PLUGIN_ID = 'plugin.video.bluesky'
PLUGIN_NAME = 'BlueSky'
PLUGIN_VERSION = '1.0.0'
PLUGIN_URL = sys.argv[0]
PLUGIN_HANDLE = int(sys.argv[1])
BASE_URL = 'https://bsky.social/xrpc/'

# Load login credentials
def load_credentials():
    login_file = os.path.join(os.path.dirname(__file__), 'login.txt')
    if os.path.exists(login_file):
        with open(login_file, 'r') as f:
            lines = f.readlines()
            if len(lines) >= 2:
                return lines[0].strip(), lines[1].strip()
    return None, None

# Authenticate with BlueSky using app password
def authenticate(username, app_password):
    url = BASE_URL + 'com.atproto.server.createSession'
    data = {
        'identifier': username,
        'password': app_password  # Use app password here
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        xbmcgui.Dialog().ok(PLUGIN_NAME, 'Authentication failed. Error: {}'.format(str(e)))
        return None

# Fetch posts from BlueSky
def fetch_posts(session):
    url = BASE_URL + 'app.bsky.feed.getTimeline'
    headers = {
        'Authorization': 'Bearer ' + session['accessJwt']
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json().get('feed', [])
    except requests.exceptions.RequestException as e:
        xbmcgui.Dialog().ok(PLUGIN_NAME, 'Failed to fetch posts. Error: {}'.format(str(e)))
        return []

# Display posts in XBMC
def display_posts(posts):
    for post in posts:
        author = post['post']['author']['handle']
        text = post['post']['record']['text']
        title = "{}: {}".format(author, text)  # Python 2.7 compatible string formatting
        list_item = xbmcgui.ListItem(title)
        xbmcplugin.addDirectoryItem(PLUGIN_HANDLE, PLUGIN_URL, list_item, isFolder=False)
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)

# Main function
def main():
    username, app_password = load_credentials()
    if not username or not app_password:
        xbmcgui.Dialog().ok(PLUGIN_NAME, 'Please enter your BlueSky username and app password in login.txt.')
        return

    session = authenticate(username, app_password)
    if not session:
        return

    posts = fetch_posts(session)
    if posts:
        display_posts(posts)

if __name__ == '__main__':
    main()
