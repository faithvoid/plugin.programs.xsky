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
import urlparse
from datetime import datetime, timedelta

# Plugin constants
PLUGIN_ID = 'plugin.video.xSky'
PLUGIN_NAME = 'xSky'
PLUGIN_VERSION = '1.0.0'
PLUGIN_URL = sys.argv[0]
PLUGIN_HANDLE = int(sys.argv[1])
BASE_URL = 'https://bsky.social/xrpc/'
CHAT_URL = 'https://api.bsky.chat/xrpc/'
PAGE_SIZE = 25  # Number of posts per page

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

# Fetch followers from BlueSky
def fetch_followers(session):
    url = BASE_URL + 'app.bsky.graph.getFollowers'
    headers = {
        'Authorization': 'Bearer ' + session['accessJwt']
    }
    params = {
        'actor': session['handle']
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json().get('followers', [])
    except requests.exceptions.RequestException as e:
        xbmcgui.Dialog().ok(PLUGIN_NAME, 'Failed to fetch followers. Error: {}'.format(str(e)))
        return []

# Fetch following from BlueSky
def fetch_following(session):
    url = BASE_URL + 'app.bsky.graph.getFollows'
    headers = {
        'Authorization': 'Bearer ' + session['accessJwt']
    }
    params = {
        'actor': session['handle']
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json().get('follows', [])
    except requests.exceptions.RequestException as e:
        xbmcgui.Dialog().ok(PLUGIN_NAME, 'Failed to fetch following. Error: {}'.format(str(e)))
        return []

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
def display_posts(posts, cursor, action):
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
        next_page_url = "{}?action={}&cursor={}".format(PLUGIN_URL, action, cursor)
        list_item = xbmcgui.ListItem("Next Page >>")
        xbmcplugin.addDirectoryItem(PLUGIN_HANDLE, next_page_url, list_item, isFolder=True)
    
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)

# Display notifications in XBMC
def display_notifications(notifications):
    for notification in notifications:
        reason = notification.get('reason', 'No Title')
        user_handle = notification.get('author', {}).get('handle', 'Unknown user')
        message = notification.get('record', {}).get('text', 'No additional information')
        title = u"{}: {} - {}".format(reason.capitalize(), user_handle, message)
        list_item = xbmcgui.ListItem(title)
        xbmcplugin.addDirectoryItem(PLUGIN_HANDLE, PLUGIN_URL, list_item, isFolder=False)
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)

# Display followers or following in XBMC
def display_user_list(users):
    for user in users:
        user_handle = user.get('handle', 'Unknown user')
        display_name = user.get('displayName', 'No Name')
        title = u"{} ({})".format(display_name, user_handle)  # Use Unicode string formatting
        url = "{}?action=profile&user_handle={}".format(PLUGIN_URL, user_handle)
        list_item = xbmcgui.ListItem(title)
        xbmcplugin.addDirectoryItem(PLUGIN_HANDLE, url, list_item, isFolder=True)
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)

# Create a new post
def create_post(session):
    keyboard = xbmc.Keyboard('', 'Enter your post')
    keyboard.doModal()
    if keyboard.isConfirmed():
        post_text = keyboard.getText()
        
        # trailing "Z" is preferred over "+00:00"
        now = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        post = {
            "$type": "app.bsky.feed.post",
            "text": post_text,
            "createdAt": now,
        }

        url = BASE_URL + 'com.atproto.repo.createRecord'
        headers = {
            'Authorization': 'Bearer ' + session['accessJwt']
        }
        data = {
            'repo': session['did'],
            'collection': 'app.bsky.feed.post',
            'record': post
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raise an error for bad status codes
            xbmcgui.Dialog().ok(PLUGIN_NAME, 'Post created successfully!')
        except requests.exceptions.RequestException as e:
            xbmcgui.Dialog().ok(PLUGIN_NAME, 'Failed to create post. Error: {}'.format(str(e)))

# Create a new post with media
def create_post_media(session):
    keyboard = xbmc.Keyboard('', 'Enter your post')
    keyboard.doModal()
    if keyboard.isConfirmed():
        post_text = keyboard.getText()
        
        # trailing "Z" is preferred over "+00:00"
        now = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        # Prompt user to select image files
        dialog = xbmcgui.Dialog()
        image_paths = []
        while True:
            image_path = dialog.browse(1, 'Select Image', 'files', '.jpg|.jpeg|.png|.webp', False, False, '')
            if image_path:
                image_paths.append(image_path)
                if len(image_paths) >= 4:  # Limit to 4 images
                    break
                if not dialog.yesno(PLUGIN_NAME, 'Do you want to add another image?'):
                    break
            else:
                break

        # Upload images and prepare the media structure
        images = []
        for image_path in image_paths:
            with open(image_path, 'rb') as f:
                img_bytes = f.read()
            # this size limit is specified in the app.bsky.embed.images lexicon
            if len(img_bytes) > 1000000:
                xbmcgui.Dialog().ok(PLUGIN_NAME, 'Image file size too large. 1000000 bytes (1MB) maximum, got: {}'.format(len(img_bytes)))
                return
            blob = upload_file(BASE_URL, session['accessJwt'], image_path, img_bytes)
            images.append({"alt": "", "image": blob})

        post = {
            "$type": "app.bsky.feed.post",
            "text": post_text,
            "createdAt": now,
            "embed": {
                "$type": "app.bsky.embed.images",
                "images": images
            }
        }

        url = BASE_URL + 'com.atproto.repo.createRecord'
        headers = {
            'Authorization': 'Bearer ' + session['accessJwt']
        }
        data = {
            'repo': session['did'],
            'collection': 'app.bsky.feed.post',
            'record': post
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raise an error for bad status codes
            xbmcgui.Dialog().ok(PLUGIN_NAME, 'Post created successfully!')
        except requests.exceptions.RequestException as e:
            xbmcgui.Dialog().ok(PLUGIN_NAME, 'Failed to create post. Error: {}'.format(str(e)))

# Function to upload files
def upload_file(base_url, access_token, filename, img_bytes):
    suffix = filename.split(".")[-1].lower()
    mimetype = "application/octet-stream"
    if suffix in ["png"]:
        mimetype = "image/png"
    elif suffix in ["jpeg", "jpg"]:
        mimetype = "image/jpeg"
    elif suffix in ["webp"]:
        mimetype = "image/webp"

    resp = requests.post(
        base_url + "com.atproto.repo.uploadBlob",
        headers={
            "Content-Type": mimetype,
            "Authorization": "Bearer " + access_token,
        },
        data=img_bytes,
    )
    resp.raise_for_status()
    return resp.json()["blob"]
    
# Display menu in XBMC
def display_menu():
    menu_items = [
        ("Home", "home"),
#        ("Search", "search"),
        ("Notifications", "notifications"),
        ("Followers", "followers"),
        ("Following", "following"),
        ("Profile", "profile"),
        ("Post", "create_post"),
        ("Post (Image)", "create_post_media")
    ]
    
    for item in menu_items:
        title, endpoint = item
        url = "{}?action={}".format(PLUGIN_URL, endpoint)
        list_item = xbmcgui.ListItem(title)
        xbmcplugin.addDirectoryItem(PLUGIN_HANDLE, url, list_item, isFolder=True)
    
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)

# Handle actions based on menu selection
def handle_action(action, session, user_handle, cursor=None):
    if action == "home":
        posts, cursor = fetch_posts(session, cursor)
        if posts:
            display_posts(posts, cursor, action)
    elif action == "search":
        keyboard = xbmc.Keyboard('', 'Enter search query')
        keyboard.doModal()
        if keyboard.isConfirmed():
            query = keyboard.getText()
            posts, cursor = search_posts(session, query, cursor)
            if posts:
                display_posts(posts, cursor, action)
    elif action == "notifications":
        notifications = fetch_notifications(session)
        if notifications:
            display_notifications(notifications)
    elif action == "followers":
        followers = fetch_followers(session)
        if followers:
            display_user_list(followers)
    elif action == "following":
        following = fetch_following(session)
        if following:
            display_user_list(following)
    elif action == "profile":
        posts, cursor = fetch_user_posts(session, user_handle, cursor)
        if posts:
            display_posts(posts, cursor, action)
    elif action == "create_post":
        create_post(session)
    elif action == "create_post_media":
        create_post_media(session)
    else:
        display_menu()

# Main function
def main():
    action = None
    cursor = None
    user_handle = None

    # Parse action, cursor, and user_handle from plugin arguments if available
    if len(sys.argv) > 2:
        params = dict(urlparse.parse_qsl(sys.argv[2][1:]))
        action = params.get('action')
        cursor = params.get('cursor')
        user_handle = params.get('user_handle')

    username, app_password = load_credentials()
    if not username or not app_password:
        xbmcgui.Dialog().ok(PLUGIN_NAME, 'Please enter your BlueSky username and app password in login.txt.')
        return

    session = authenticate(username, app_password)
    if not session:
        return

    if not user_handle:
        user_handle = session.get('handle', 'unknown_user')
    handle_action(action, session, user_handle, cursor)

if __name__ == '__main__':
    main()
