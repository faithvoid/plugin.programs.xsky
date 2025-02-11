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
- Invite and accept invites from fellow XBMC users to games via "Invite to Game" in chat!

## Not Working:
- Viewing Images / Videos / Thumbnails
- Search
- Feeds / Lists
- Emojis (slightly breaks timestamps on the message with the emoji)

## TODO:
- Fix thumbnails for posts
- Show user avatar as thumbnail if the image doesn't contain media (currently shows avatars in Following / Followers, but is glitchy in posts / profiles)
- Add pagination to messages to reduce load times
- Improve visual language (try to match 1:1 to the Bluesky website where possible)
- Add notification / chat indicators (ie; "Chat (5)" / "Notifications (2)")
- Add some way to differentiate between a post and a reply
- Add reply chains(?)
- Add "Follow / Unfollow User", "Block User", "Reply to User" & "Message User" as context menu options
- Store login data somewhere that isn't just a plaintext file?
- [Find a way to leverage Bluesky's chat functionality for an IM service(?)](https://github.com/faithvoid/plugin.programs.xchat)
- Implement group DMs / media DMs once they're implemented into Bluesky
- Add "Install Game" option to Settings (aka writing a game name and path to games.txt)
- Ask user if they'd like to launch game when inviting user, and when accepting an invitation, if the user doesn't have the game 'installed', asks if they'd like to select the directory where the game is located.
