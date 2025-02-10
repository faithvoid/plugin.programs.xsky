# xSky - Bluesky client for XBMC4Xbox

A functional, decentralized and easy to use social media network, right on your Xbox.

![icon](icon.png)

## Screenshots:
![1](screenshots/1.png)
![2](screenshots/2.png)
![3](screenshots/3.png)
![4](screenshots/4.png)


## Install:
- Before downloading, make sure you're on XBMC 3.6-DEV-r33046 or later, as this most likely requires up to date TLS/SSL libraries!
- Download latest release .zip
- Extract the .zip file and edit "login.txt" to contain your full username (ie; username.bsky.social or username.custom.domain) and app password (do not use your actual password!)
- Copy the xSky folder to Q:/scripts/plugins/programs
- (Optional) if using a non-Bluesky AT protocol site, you'll have to modify the BASE_URL in default.py to point at that site! Support outside of Bluesky is entirely unsupported, but testing & contributing is encouraged!
- Run the add-on and enjoy!

## Working:
- Logging in (via inserting your credentials into login.txt)
- Viewing Home feed
- Viewing notifications
- Viewing profile
- Viewing Followers / Following + user profiles
- Posting

## Not Working:
- Images / Videos / Thumbnails
- Search
- Feeds / Lists

## TODO:
- Add profile information (ie; name + avatar - bio) as first 2 options when viewing a profile
- Add timestamps to posts
- Add dialog windows to view full posts, as currently they're just list items.
- Add some way to differentiate between a post and a reply
- Add "Follow / Unfollow User", "Block User" & "Reply to User" as context menu options
- Add reply chains(?)
- Store login data somewhere that isn't just a plaintext file?
- Find a way to leverage Bluesky's chat functionality for an IM service(?)
- Make "Post with Image" or "Post with Video" option for uploading files (this may end up being incredibly janky but a nice QoL thing to have)
- Show user avatar as thumbnail if the image doesn't contain media(?)
- Add notification system that alerts the user as to whenever they get a reply / follow / message while outside of the plugin (this will probably have to be it's own plugin)
