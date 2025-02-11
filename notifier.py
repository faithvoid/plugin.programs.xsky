import xbmc
import xbmcgui
import requests
import os
import time
import datetime

# Script constants
SCRIPT_NAME = 'xChat'
BASE_URL = 'https://bsky.social/xrpc/'
CHAT_URL = 'https://api.bsky.chat/xrpc/'
CHECK_INTERVAL = 5  # Interval in seconds to check for new messages
LOGIN_FILE = os.path.join(os.path.dirname(__file__), 'login.txt')

# Load login credentials
def load_credentials():
    if os.path.exists(LOGIN_FILE):
        with open(LOGIN_FILE, 'r') as f:
            lines = f.readlines()
            if len(lines) >= 2:
                return lines[0].strip(), lines[1].strip()
    return None, None

# Authenticate with BlueSky using app password
def authenticate(username, app_password):
    url = BASE_URL + 'com.atproto.server.createSession'
    data = {
        'identifier': username,
        'password': app_password
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        xbmc.log("{}: Authentication failed. Error: {}".format(SCRIPT_NAME, str(e)), xbmc.LOGERROR)
        return None

# Fetch conversations from BlueSky
def fetch_conversations(session):
    url = CHAT_URL + 'chat.bsky.convo.listConvos'
    headers = {
        'Authorization': 'Bearer ' + session['accessJwt']
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
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
        xbmc.log("{}: Failed to fetch conversations. Error: {}".format(SCRIPT_NAME, str(e)), xbmc.LOGERROR)
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
        response.raise_for_status()
        return response.json().get('messages', [])
    except requests.exceptions.RequestException as e:
        xbmc.log("{}: Failed to fetch messages. Error: {}".format(SCRIPT_NAME, str(e)), xbmc.LOGERROR)
        return []

# Main service loop
def main():
    username, app_password = load_credentials()
    if not username or not app_password:
        xbmc.log("{}: Please enter your BlueSky username and app password in login.txt.".format(SCRIPT_NAME), xbmc.LOGERROR)
        return

    session = authenticate(username, app_password)
    if not session:
        return

    old_message_ids = set()
    while True:
        convos = fetch_conversations(session)
        for convo in convos:
            messages = fetch_messages(session, convo.get('id'))
            for message in messages:
                message_id = message.get('id')
                if message_id not in old_message_ids:
                    old_message_ids.add(message_id)
                    user_handle = message.get('sender', {}).get('handle', 'Unknown')
                    text = message.get('text', 'No text')
                    xbmc.executebuiltin('XBMC.Notification("New message from {0}", "{1}", 5000, "")'.format(user_handle, text))
        
        xbmc.sleep(CHECK_INTERVAL * 1000)

if __name__ == '__main__':
    main()
