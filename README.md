# Immich_Notify
This python script checks defined immich shared albums for added items and sends notifications via ntfy app.

# Functionality
Docker container runs python script every 30 minutes.
If FILEPATH doesn't exist, it will first query albums for current item counts and create the file.
If FILEPATH does exist, it will load saved item counts, query albums for current counts.
If there are new items added, a notification will be published to NTFYURL topic.

# Setup
Recommended setup via docker-compose

## docker-compose.yml
```
version: "1.0"

services:
  immich_notify:
    image: pierson07/immich_notify:latest
    container_name: immich_notify
    env_file:
      - stack.env
    volumes:
      - /path/to/data.txt:/path/to/data.txt # optional, use to retain data through redeployment
    restart: unless-stopped
```

## stack.env
```
# Base url to access API
# example: http://192.168.1.100:
BASEURL=<Internal Immich URL to lookup album info>

# External url to access albums via notification link
# example: https://immich.fakeurl.com
EXTERNALURL=<External Immich URL for notification link>

# Immich API Key
IMMICHKEY=<Immich API Key>

# File to store album item counts
FILEPATH=./data.txt

# Dictionary with album id(s) and desired notification topic(s)
# Can all be the same topic or divide up as desired
ALBUMS={'albumID1': 'topic1','albumID2': 'topic2', ...}

# ntfy URL to send notifications to
# ntfy can be self hosted or use free or paid teirs of https://ntfy.sh
NTFYURL=<ntfy URL>

# Icon to use for ntfy notification
NTFYICON=https://raw.githubusercontent.com/immich-app/immich/53adb0c5150cc8af7c551f7a3059df83c45c2930/design/immich-logo.svg
```
