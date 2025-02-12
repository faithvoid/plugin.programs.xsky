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
import time
import datetime
import re
from datetime import timedelta

# Plugin constants
PLUGIN_ID = 'plugin.video.xSky'
PLUGIN_NAME = 'xSky'
PLUGIN_VERSION = '1.0.0'
PLUGIN_URL = sys.argv[0]
PLUGIN_HANDLE = int(sys.argv[1])
BASE_URL = 'https://bsky.social/xrpc/'
CHAT_URL = 'https://api.bsky.chat/xrpc/'
PAGE_SIZE = 25  # Number of posts per page
TIMEZONE_OFFSET = -5  # Manually enter the time zone difference from UTC (e.g., -5 for EST)

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

def fetch_profile(session, user_handle):
    url = BASE_URL + 'app.bsky.actor.getProfile'
    headers = {
        'Authorization': 'Bearer ' + session['accessJwt']
    }
    params = {
        'actor': user_handle
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        xbmcgui.Dialog().ok(PLUGIN_NAME, 'Failed to fetch profile. Error: {}'.format(str(e)))
        return None

# Display posts in XBMC
def display_posts(posts, cursor, action, profile=None):
    if profile:
        # Display profile name with avatar as thumbnail
        name = profile.get('displayName', 'Unknown')
        avatar = profile.get('avatar', None)
        bio = profile.get('description', 'No bio available').replace('\n', ' | ')
        blank = profile.get('', '-')
        
        name_item = xbmcgui.ListItem(name)
        if avatar:
            name_item.setThumbnailImage(avatar)
        xbmcplugin.addDirectoryItem(PLUGIN_HANDLE, PLUGIN_URL, name_item, isFolder=False)
        
        # Display profile bio
        bio_item = xbmcgui.ListItem(bio, blank)
        xbmcplugin.addDirectoryItem(PLUGIN_HANDLE, PLUGIN_URL, bio_item, isFolder=False)

        # Display blank space
        bio_item = xbmcgui.ListItem(blank)
        xbmcplugin.addDirectoryItem(PLUGIN_HANDLE, PLUGIN_URL, bio_item, isFolder=False)

    for post in posts:
        # Ensure the post structure is as expected
        if 'post' in post:
            author = post['post']['author']['handle']
            text = post['post']['record']['text']
            
            # Add timestamp
            created_at = post['post']['record']['createdAt']
            try:
                utc_time = datetime.datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
            except ValueError:
                try:
                    utc_time = datetime.datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
                except ValueError:
                    utc_time = datetime.datetime.strptime(created_at[:-6], '%Y-%m-%dT%H:%M:%S.%f')
            
            # Calculate elapsed time
            now = datetime.datetime.utcnow()
            elapsed_time = now - utc_time
            total_seconds = int(elapsed_time.total_seconds())
            
            if total_seconds < 60:
                time_suffix = "- {}s".format(total_seconds)
            elif total_seconds < 3600:
                minutes_ago = total_seconds // 60
                time_suffix = "- {}m".format(minutes_ago)
            elif total_seconds < 86400:
                hours_ago = total_seconds // 3600
                time_suffix = "- {}h".format(hours_ago)
            elif total_seconds < 2592000:
                days_ago = total_seconds // 86400
                time_suffix = "- {}d".format(days_ago)
            elif total_seconds < 31536000:
                months_ago = total_seconds // 2592000
                time_suffix = "- {}mo".format(months_ago)
            else:
                years_ago = total_seconds // 31536000
                time_suffix = "- {}y".format(years_ago)
            
            # Get replies, likes, and reshares counts
            replies_count = post['post'].get('replyCount', 0)
            likes_count = post['post'].get('likeCount', 0)
            reshares_count = post['post'].get('repostCount', 0)
            
            counts_suffix = "({} replies, {} likes, {} reshares)".format(replies_count, likes_count, reshares_count)
            
            title = u"{}: {} {} {}".format(author, text, counts_suffix, time_suffix)  # Use Unicode string formatting
            
            # Check if there are images attached to the post
            images = post['post']['record'].get('images', [])
            thumbnail = images[0]['url'] if images else None
            
            list_item = xbmcgui.ListItem(title)
            if thumbnail:
                list_item.setThumbnailImage(thumbnail)

            # Add context menu to view the full post
            context_menu = [(u'View Post', u'XBMC.RunPlugin({}?action=view_post&author={}&text={})'.format(PLUGIN_URL, author, text))]
            list_item.addContextMenuItems(context_menu)
            
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
        message = notification.get('record', {}).get('text', '')
        title = u"{}: {} - {}".format(reason.capitalize(), user_handle, message)
        list_item = xbmcgui.ListItem(title)
        xbmcplugin.addDirectoryItem(PLUGIN_HANDLE, PLUGIN_URL, list_item, isFolder=False)
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)

# Display followers or following in XBMC
def display_user_list(users):
    for user in users:
        user_handle = user.get('handle', 'Unknown user')
        display_name = user.get('displayName', 'No Name')
        avatar = user.get('avatar', None)
        
        title = u"{} ({})".format(display_name, user_handle)  # Use Unicode string formatting
        url = "{}?action=profile&user_handle={}".format(PLUGIN_URL, user_handle)
        list_item = xbmcgui.ListItem(title)
        
        if avatar:
            list_item.setThumbnailImage(avatar)
        
        xbmcplugin.addDirectoryItem(PLUGIN_HANDLE, url, list_item, isFolder=True)
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)


# Resolve DID to URL for mention purposes.
def resolve_did(handle, session):
    url = BASE_URL + 'com.atproto.identity.resolveHandle'
    headers = {
        'Authorization': 'Bearer ' + session['accessJwt'],
        'Content-Type': 'application/json'
    }
    data = {
        'handle': handle
    }
    try:
        response = requests.get(url, headers=headers, params=data)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json().get('did')
    except requests.exceptions.RequestException as e:
        xbmcgui.Dialog().ok(PLUGIN_NAME, 'Failed to resolve DID. Error: {}'.format(str(e)))
        return None

# Detects mention / tag facets and hyperlinks them accordingly.
def detect_facets(text, session):
    facets = []
    utf16_text = text

    def utf16_index_to_utf8_index(i):
        return len(utf16_text[:i].encode('utf-8'))

    # Detect mentions
    mention_pattern = re.compile(r'(^|\s|\()(@[a-zA-Z0-9.-]+)(\b)')
    for match in mention_pattern.finditer(utf16_text):
        mention = match.group(2)
        handle = mention[1:]  # Remove the '@' character
        start = match.start(2)
        end = match.end(2)
        did = resolve_did(handle, session)
        if did:
            facets.append({
                'index': {
                    'byteStart': utf16_index_to_utf8_index(start),
                    'byteEnd': utf16_index_to_utf8_index(end),
                },
                'features': [{
                    '$type': 'app.bsky.richtext.facet#mention',
                    'did': did
                }]
            })

    # Detect hashtags
    hashtag_pattern = re.compile(r'(#[^\d\s]\S*)')
    for match in hashtag_pattern.finditer(utf16_text):
        hashtag = match.group(1)
        start = match.start(1)
        end = match.end(1)
        facets.append({
            'index': {
                'byteStart': utf16_index_to_utf8_index(start),
                'byteEnd': utf16_index_to_utf8_index(end),
            },
            'features': [{
                '$type': 'app.bsky.richtext.facet#tag',
                'tag': hashtag[1:]
            }]
        })

    return facets

# Create a new post
def create_post(session):
    keyboard = xbmc.Keyboard('', 'Enter your post')
    keyboard.doModal()
    if keyboard.isConfirmed():
        post_text = keyboard.getText()
        
        # trailing "Z" is preferred over "+00:00"
        now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        
        # Detect facets for hashtags and mentions
        facets = detect_facets(post_text, session)

        post = {
            "$type": "app.bsky.feed.post",
            "text": post_text,
            "facets": facets,
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
        now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        
        # Detect facets for hashtags and mentions
        facets = detect_facets(post_text, session)

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
            "facets": facets,
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

# Fetch conversations from BlueSky
def fetch_conversations(session):
    url = CHAT_URL + 'chat.bsky.convo.listConvos'
    headers = {
        'Authorization': 'Bearer ' + session['accessJwt']
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        convos = response.json().get('convos', [])
        
        # Add the handle of the user messaging to each conversation
        for convo in convos:
            participants = convo.get('members', [])
            convo['user_handle'] = next(
                (participant['handle'] for participant in participants if participant['handle'] != session['handle']),
                'Unknown'
            )
        
        return convos
    except requests.exceptions.RequestException as e:
        xbmcgui.Dialog().ok(PLUGIN_NAME, 'Failed to fetch conversations. Error: {}'.format(str(e)))
        return []

# Fetch messages for a conversation from BlueSky
def fetch_messages(session, convo_id):
    url = CHAT_URL + 'chat.bsky.convo.getMessages'
    headers = {
        'Authorization': 'Bearer ' + session['accessJwt']
    }
    params = {
        'convoId': convo_id
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        messages = response.json().get('messages', [])
        
        # Collect all DIDs to fetch profiles in bulk
        dids = {message['sender']['did'] for message in messages if 'sender' in message and 'did' in message['sender']}
        profiles = {did: fetch_profile(session, did) for did in dids}
        
        # Ensure each message has the sender's handle
        for message in messages:
            if 'sender' in message and 'did' in message['sender']:
                sender_profile = profiles.get(message['sender']['did'], {})
                message['sender']['handle'] = sender_profile.get('handle', 'Unknown')
        
        return messages
    except requests.exceptions.RequestException as e:
        xbmcgui.Dialog().ok(PLUGIN_NAME, 'Failed to fetch messages. Error: {}'.format(str(e)))
        return []

# Display conversations in XBMC
def display_conversations(session, conversations):
    for convo in conversations:
        participant = convo.get('user_handle', 'Unknown')
        last_message = convo.get('lastMessage', {}).get('text', 'No message')
        sent_at = convo.get('lastMessage', {}).get('sentAt', 'No date')

        # Format the timestamp
        try:
            utc_time = datetime.datetime.strptime(sent_at, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            utc_time = datetime.datetime.strptime(sent_at, '%Y-%m-%dT%H:%M:%SZ')

        now = datetime.datetime.utcnow()
        elapsed_time = now - utc_time
        total_seconds = int(elapsed_time.total_seconds())

        if total_seconds < 60:
            time_suffix = "{}s".format(total_seconds)
        elif total_seconds < 3600:
            minutes_ago = total_seconds // 60
            time_suffix = "{}m".format(minutes_ago)
        elif total_seconds < 86400:
            hours_ago = total_seconds // 3600
            time_suffix = "{}h".format(hours_ago)
        elif total_seconds < 2592000:
            days_ago = total_seconds // 86400
            time_suffix = "{}d".format(days_ago)
        elif total_seconds < 31536000:
            months_ago = total_seconds // 2592000
            time_suffix = "{}mo".format(months_ago)
        else:
            years_ago = total_seconds // 31536000
            time_suffix = "{}y".format(years_ago)

        # Fetch the profile to get the avatar
        profile = fetch_profile(session, participant)
        avatar = profile.get('avatar', None)

        title = u"[{}] - {} - {}".format(participant, last_message, time_suffix)  # Use Unicode string formatting
        url = "{}?action=messages&convo_id={}".format(PLUGIN_URL, convo.get('id'))
        list_item = xbmcgui.ListItem(title)

        if avatar:
            list_item.setThumbnailImage(avatar)

        xbmcplugin.addDirectoryItem(PLUGIN_HANDLE, url, list_item, isFolder=True)
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)

# Display messages in XBMC
def display_messages(session, convo_id, messages):
    # Add a "Reply" option as the first list item
    reply_url = "{}?action=reply&convo_id={}".format(PLUGIN_URL, convo_id)
    reply_item = xbmcgui.ListItem("Reply")
    xbmcplugin.addDirectoryItem(PLUGIN_HANDLE, reply_url, reply_item, isFolder=False)
    
    for message in messages:
        text = message.get('text', 'No text')
        sent_at = message.get('sentAt', 'No date')
        user_handle = message.get('sender', {}).get('handle', 'Unknown')

        # Format the timestamp
        try:
            utc_time = datetime.datetime.strptime(sent_at, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            utc_time = datetime.datetime.strptime(sent_at, '%Y-%m-%dT%H:%M:%SZ')

        now = datetime.datetime.utcnow()
        elapsed_time = now - utc_time
        total_seconds = int(elapsed_time.total_seconds())

        if total_seconds < 60:
            time_suffix = "{}s".format(total_seconds)
        elif total_seconds < 3600:
            minutes_ago = total_seconds // 60
            time_suffix = "{}m".format(minutes_ago)
        elif total_seconds < 86400:
            hours_ago = total_seconds // 3600
            time_suffix = "{}h".format(hours_ago)
        elif total_seconds < 2592000:
            days_ago = total_seconds // 86400
            time_suffix = "{}d".format(days_ago)
        elif total_seconds < 31536000:
            months_ago = total_seconds // 2592000
            time_suffix = "{}mo".format(months_ago)
        else:
            years_ago = total_seconds // 31536000
            time_suffix = "{}y".format(years_ago)

        # Display formatted message
        title = u"[{}] - {} - {}".format(user_handle, text, time_suffix)
        list_item = xbmcgui.ListItem(title)
        xbmcplugin.addDirectoryItem(PLUGIN_HANDLE, PLUGIN_URL, list_item, isFolder=False)
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)

# Function to reply to a conversation
def reply_to_conversation(session, convo_id):
    keyboard = xbmc.Keyboard('', 'Enter your reply')
    keyboard.doModal()
    if keyboard.isConfirmed():
        reply_text = keyboard.getText()
        # trailing "Z" is preferred over "+00:00"
        now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        message = {
            "$type": "chat.bsky.convo.message",
            "text": reply_text,
            "createdAt": now,
        }
        url = CHAT_URL + 'chat.bsky.convo.sendMessage'
        headers = {
            'Authorization': 'Bearer ' + session['accessJwt']
        }
        data = {
            'convoId': convo_id,
            'message': message
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raise an error for bad status codes
            xbmcgui.Dialog().ok(PLUGIN_NAME, 'Reply sent successfully!')
        except requests.exceptions.RequestException as e:
            xbmcgui.Dialog().ok(PLUGIN_NAME, 'Failed to send reply. Error: {}'.format(str(e)))
    
# Display menu in XBMC
def display_menu():
    menu_items = [
        ("Home", "home"),
#        ("Search", "search"),
        ("Notifications", "notifications"),
        ("Chat", "conversations"),
#        ("Feeds", "feeds"),
#        ("Lists", "lists"),
#        ("Search", "conversations"),
        ("Followers", "followers"),
        ("Following", "following"),
        ("Post", "create_post"),
        ("Post (Image)", "create_post_media"),
        ("Profile", "profile"),
        ("Settings", "settings")
    ]
    
    for item in menu_items:
        title, endpoint = item
        url = "{}?action={}".format(PLUGIN_URL, endpoint)
        list_item = xbmcgui.ListItem(title)
        xbmcplugin.addDirectoryItem(PLUGIN_HANDLE, url, list_item, isFolder=True)
    
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)

# Display settings menu
def display_settings():
    settings_items = [
        ("Enable Notifications", "enable_notifications"),
        ("Disable Notifications", "disable_notifications")
    ]
    
    for item in settings_items:
        title, endpoint = item
        url = "{}?action={}".format(PLUGIN_URL, endpoint)
        list_item = xbmcgui.ListItem(title)
        xbmcplugin.addDirectoryItem(PLUGIN_HANDLE, url, list_item, isFolder=False)
    
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)

# Execute action to enable/disable notifier
def execute_action(action):
    if action == "enable_notifications":
        run_notifier()
    if action == "disable_notifications":
        stop_notifier()

# Run notifier.py
def run_notifier():
    script_path = os.path.join(os.path.dirname(__file__), 'notifier.py')
    xbmc.executebuiltin('RunScript({})'.format(script_path))

# Stop notifier.py
def stop_notifier():
    script_path = os.path.join(os.path.dirname(__file__), 'notifier.py')
    xbmc.executebuiltin('RunScript({})'.format(script_path))

# Handle actions based on menu selection
def handle_action(action, session, user_handle, cursor=None, convo_id=None):
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
        profile = fetch_profile(session, user_handle)
        posts, cursor = fetch_user_posts(session, user_handle, cursor)
        if posts:
            display_posts(posts, cursor, action, profile)
    elif action == "create_post":
        create_post(session)
    elif action == "create_post_media":
        create_post_media(session)
    elif action == "conversations":
        conversations = fetch_conversations(session)
        if conversations:
            display_conversations(session, conversations)
    elif action == "messages":
        if not convo_id:
            convo_id = sys.argv[2].split('convo_id=')[1].split('&')[0]
        messages = fetch_messages(session, convo_id)
        display_messages(session, convo_id, messages)
    elif action == "view_post":
        author = unicode(sys.argv[2].split('author=')[1].split('&')[0], 'utf-8')
        text = unicode(sys.argv[2].split('text=')[1], 'utf-8')
        # Split text into multiple lines if necessary
        split_text = [text[i:i+64] for i in range(0, len(text), 64)]
        xbmcgui.Dialog().ok(author, *split_text)
    elif action == "reply":
        convo_id = sys.argv[2].split('convo_id=')[1].split('&')[0]
        reply_to_conversation(session, convo_id)
    elif action == "settings":
        display_settings()
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
    if action in ["enable_notifications"]:
        execute_action(action)
    else:
        handle_action(action, session, user_handle, cursor)

if __name__ == '__main__':
    main()
