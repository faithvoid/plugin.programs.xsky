#   ______ ___  _____ _____ _   _       __  _   _  _____ ___________ 
#   |  ___/ _ \|_   _|_   _| | | |     / / | | | ||  _  |_   _|  _  \
#   | |_ / /_\ \ | |   | | | |_| |    / /  | | | || | | | | | | | | |
#   |  _||  _  | | |   | | |  _  |   / /   | | | || | | | | | | | | |
#   | |  | | | |_| |_  | | | | | |  / /    \ \_/ /\ \_/ /_| |_| |/ / 
#   \_|  \_| |_/\___/  \_/ \_| |_/ /_/      \___/  \___/ \___/|___/  
#                  xSky - Bluesky client for XBMC4Xbox

import xbmc
import xbmcgui
import xbmcplugin
import os
import sys
import requests
import json

# Plugin constants
PLUGIN_ID = 'plugin.video.xSky'
PLUGIN_NAME = 'xSky'
PLUGIN_VERSION = '1.0.0'
PLUGIN_URL = sys.argv[0]
PLUGIN_HANDLE = int(sys.argv[1])
BASE_URL = 'https://bsky.social/xrpc/'
PAGE_SIZE = 10  # Number of posts per page

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
def fetch_posts(session, cursor=None):
    url = BASE_URL + 'app.bsky.feed.getTimeline'
    headers = {
        'Authorization': 'Bearer ' + session['accessJwt']
    }
    params = {
        'limit': PAGE_SIZE,
        'cursor': cursor
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        return data.get('feed', []), data.get('cursor')
    except requests.exceptions.RequestException as e:
        xbmcgui.Dialog().ok(PLUGIN_NAME, 'Failed to fetch posts. Error: {}'.format(str(e)))
        return [], None

# Fetch notifications from BlueSky
def fetch_notifications(session):
    url = BASE_URL + 'app.bsky.notification.listNotifications'
    headers = {
        'Authorization': 'Bearer ' + session['accessJwt']
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json().get('notifications', [])
    except requests.exceptions.RequestException as e:
        xbmcgui.Dialog().ok(PLUGIN_NAME, 'Failed to fetch notifications. Error: {}'.format(str(e)))
        return []

# Fetch user posts from BlueSky
def fetch_user_posts(session, user_handle, cursor=None):
    url = BASE_URL + 'app.bsky.feed.getAuthorFeed'
    headers = {
        'Authorization': 'Bearer ' + session['accessJwt']
    }
    params = {
        'actor': user_handle,
        'limit': PAGE_SIZE,
        'cursor': cursor
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        return data.get('feed', []), data.get('cursor')
    except requests.exceptions.RequestException as e:
        xbmcgui.Dialog().ok(PLUGIN_NAME, 'Failed to fetch user posts. Error: {}'.format(str(e)))
        return [], None

# Search posts on BlueSky
def search_posts(session, query, cursor=None):
    url = BASE_URL + 'app.bsky.feed.searchPosts'
    headers = {
        'Authorization': 'Bearer ' + session['accessJwt']
    }
    params = {
        'q': query,
        'limit': PAGE_SIZE,
        'cursor': cursor
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        return data.get('posts', []), data.get('cursor')
    except requests.exceptions.RequestException as e:
        xbmcgui.Dialog().ok(PLUGIN_NAME, 'Failed to search posts. Error: {}'.format(str(e)))
        return [], None

# Display posts in XBMC
def display_posts(posts, cursor):
    for post in posts:
        # Ensure the post structure is as expected
        if 'post' in post:
            author = post['post']['author']['handle']
            text = post['post']['record']['text']
            title = u"{}: {}".format(author, text)  # Use Unicode string formatting
            
            # Check if there are images attached to the post
            images = post['post']['record'].get('images', [])
            thumbnail = images[0]['url'] if images else None
            
            list_item = xbmcgui.ListItem(title)
            if thumbnail:
                list_item.setArt({'thumb': thumbnail})
            
            xbmcplugin.addDirectoryItem(PLUGIN_HANDLE, PLUGIN_URL, list_item, isFolder=False)
    
    # Add a "Next Page" item if there are more posts
    if cursor:
        next_page_url = PLUGIN_URL + "?cursor=" + cursor
        list_item = xbmcgui.ListItem("Next Page")
        xbmcplugin.addDirectoryItem(PLUGIN_HANDLE, next_page_url, list_item, isFolder=True)
    
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)

# Display notifications in XBMC
def display_notifications(notifications):
    for notification in notifications:
        reason = notification.get('reason', 'No Title')
        user_handle = notification.get('author', {}).get('handle', 'Unknown user')
        message = notification.get('record', {}).get('text', 'No additional information')
        title = "{}: {} - {}".format(reason.capitalize(), user_handle, message)
        list_item = xbmcgui.ListItem(title)
        xbmcplugin.addDirectoryItem(PLUGIN_HANDLE, PLUGIN_URL, list_item, isFolder=False)
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)

# Create a new post
def create_post(session):
    keyboard = xbmc.Keyboard('', 'Enter your post')
    keyboard.doModal()
    if keyboard.isConfirmed():
        post_text = keyboard.getText()
        url = BASE_URL + 'app.bsky.feed.createPost'
        headers = {
            'Authorization': 'Bearer ' + session['accessJwt']
        }
        data = {
            'text': post_text
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raise an error for bad status codes
            xbmcgui.Dialog().ok(PLUGIN_NAME, 'Post created successfully!')
        except requests.exceptions.RequestException as e:
            xbmcgui.Dialog().ok(PLUGIN_NAME, 'Failed to create post. Error: {}'.format(str(e)))

# Display menu in XBMC
def display_menu():
    menu_items = [
        ("Home", "home"),
#        ("Search", "search"),
        ("Notifications", "notifications"),
#        ("Chat", "chat"),
#        ("Feeds", "feeds"),
#        ("Lists", "lists"),
        ("Profile", "profile"),
#        ("Post", "create_post") 
    ]
    
    for item in menu_items:
        title, endpoint = item
        url = "{}?action={}".format(PLUGIN_URL, endpoint)
        list_item = xbmcgui.ListItem(title)
        xbmcplugin.addDirectoryItem(PLUGIN_HANDLE, url, list_item, isFolder=True)
    
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)

# Handle actions based on menu selection
def handle_action(action, session, user_handle):
    if action == "home":
        posts, cursor = fetch_posts(session)
        if posts:
            display_posts(posts, cursor)
    elif action == "search":
        keyboard = xbmc.Keyboard('', 'Enter search query')
        keyboard.doModal()
        if keyboard.isConfirmed():
            query = keyboard.getText()
            posts, cursor = search_posts(session, query)
            if posts:
                display_posts(posts, cursor)
    elif action == "notifications":
        notifications = fetch_notifications(session)
        if notifications:
            display_notifications(notifications)
    elif action == "chat":
        xbmcgui.Dialog().ok(PLUGIN_NAME, "Chat is not yet implemented.")
    elif action == "feeds":
        xbmcgui.Dialog().ok(PLUGIN_NAME, "Feeds is not yet implemented.")
    elif action == "lists":
        xbmcgui.Dialog().ok(PLUGIN_NAME, "Lists is not yet implemented.")
    elif action == "profile":
        posts, cursor = fetch_user_posts(session, user_handle)
        if posts:
            display_posts(posts, cursor)
    elif action == "create_post":
        create_post(session)
    else:
        display_menu()

# Main function
def main():
    action = None

    # Parse action from plugin arguments if available
    if len(sys.argv) > 2:
        action = sys.argv[2].split('=')[1] if 'action=' in sys.argv[2] else None

    username, app_password = load_credentials()
    if not username or not app_password:
        xbmcgui.Dialog().ok(PLUGIN_NAME, 'Please enter your BlueSky username and app password in login.txt.')
        return

    session = authenticate(username, app_password)
    if not session:
        return

    user_handle = session.get('handle', 'unknown_user')
    handle_action(action, session, user_handle)

if __name__ == '__main__':
    main()
