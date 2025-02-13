# xSky - Bluesky / AT Protocol client for XBMC4Xbox

A functional, decentralized and easy to use social media network, right on your Xbox.

![icon](icon.png)

## Screenshots:
![1](screenshots/1.png)
![2](screenshots/2.png)
![3](screenshots/3.png)
![4](screenshots/4.png)
![4](screenshots/5.png)


## Install:
- Before downloading, make sure you're on XBMC 3.6-DEV-r33046 or later, as this most likely requires up to date TLS/SSL libraries!
- Download latest release .zip
- Extract the .zip file and edit "login.txt" to contain your full username (ie; username.bsky.social or username.custom.domain) and app password (do not use your actual password!)
- Edit "default.py" and modify "TIMEZONE_OFFSET = -5" to your local timezone relative to UTC (-5 is EST) for accurate timestamps
- Copy the xSky folder to Q:/scripts/plugins/programs
- (Optional) if using a non-Bluesky AT protocol site, you'll have to modify the BASE_URL in default.py to point at that site! Support outside of Bluesky is entirely unsupported, but testing & contributing is encouraged!
- Run the add-on and enjoy!
- (Optional) To get chat & notification pop-ups, go to "Settings" and select "Enable Notifications". The first run may take a few seconds and spam you with all of your messages at once. After this, all subsequent reruns should only show messages not previously read via XBMC, as it lists all read message IDs and usernames/handles in "messages.txt" & "handles.txt" to prevent showing already-read messages and having to fetch the username attached to each DID from the server for each individual message. Future versions will hopefully use "seenAt" instead.

## Working:
- Logging in (via inserting your credentials into login.txt)
- Viewing Home feed
- Viewing notifications
- Viewing profile
- Viewing Followers / Following + user profiles
- Making text/image posts & tagging users and hashtags in those posts
- Viewing posts as list items + dialog windows
- Sending / receiving messages
- Fetching new messages and notifications as toast notifications every 5 seconds (via notifier.py)
- Sending and receiving game invites from fellow XBMC users via "Invite to Game" in chat! (currently needs games manually added to games.txt)

## Not Working:
- Viewing Images / Videos / Thumbnails
- Search
- Feeds / Lists
- Emojis (slightly breaks timestamps on the message with the emoji)

## TODO:
- Fix thumbnails for posts & avatars in "Profiles" menu.
- Show user avatar as thumbnail if the image doesn't contain media
- Add pagination to messages to reduce load times (set to 25 message limit?)
- Improve visual language (try to match 1:1 to the Bluesky website where possible)
- Add notification / chat indicators (ie; "Chat (5)" / "Notifications (2)")
- Add some way to differentiate between a post and a reply
- Add reply chains(?)
- Add "Follow / Unfollow User", "Block User", "Reply to User" & "Message User" as context menu options
- Store login data somewhere that isn't just a plaintext file?
- [Find a way to leverage Bluesky's chat functionality for an IM service(?)](https://github.com/faithvoid/plugin.programs.xchat)
- Add "Install Game" option to Settings (aka writing a game name and path to games.txt), and if attempting to launch a game that's not 'installed', ask the user if they'd like to select the .xbe for the game to write into games.txt.
- Add the ability to edit handle / name / bio while in "Profile"
- Hardcode games.txt in both this & Cortana Server Browser to "special://profile//games.txt" so they share the same file
- Implement group DMs / media DMs once they're implemented into Bluesky
- Implement multi-account system?
