# Immich Notify
This python script checks defined immich shared albums for added items and sends notifications via ntfy app.

# Functionality
Docker container runs python script every 15 minutes by default.
If FILEPATH doesn't exist, it will first query albums for current item counts and create the file.
If FILEPATH does exist, it will load saved item counts, query albums for current counts.
If there are new items added, a notification will be published to NTFYURL topic.

![image](https://github.com/pman07/Immich_Notify/assets/56171396/7aaf9ca1-e619-4075-9e58-2ac26eeccdc9)
![image](https://github.com/pman07/Immich_Notify/assets/56171396/7c853b93-e181-4f21-a6a2-e00a18e80c6d)




# Setup
Recommended setup via docker-compose below. Once docker container is running, visit <docker ip>:5000 (by default) in browser to configure the app.

1. Configuration Setup. Fill out the following fields
```
  Immich Local URL: local path to hit API (ex: 192.168.1.1:2283)
  Immich External URL: external path for notification link (ex: immich.com)
  Immich API Key: api key for Immich (ex: abcdefghijkl)
  ntfy URL: path to your ntfy instance (ex: ntfy.sh or 192.168.1.1:8080)
  ntfy Icon URL: path to image for ntfy notifications (ex: https://raw.githubusercontent.com/immich-app/immich/main/design/immich-logo.png)
  ntfy email: email address for ntfy email notifications (OPTIONAL)
  ntfy email tag: email tag for ntfy email notification Emoji/Tag see https://docs.ntfy.sh/emojis/ (OPTIONAL)
  ntfy authorization: ntfy Basic Authorization Token (OPTIONAL)
  
```
2. Click "Save Config"
3. Click "Get Shared Albums"
4. Check the Shared Albums you want to monitor and fill out the topic(s) for each album
5. Click "Save Shared Albums"
6. Update the Notification Period (if desired). By default application will run every 15 minutes.
7. Click "Start Notifications App"

## Just the Notify Script docker-compose.yml
```
version: "3.8"

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
## Self-Hosted NTFY and Notify Script docker-compose.yml
```
version: "3.8"

services:
  immich_notify:
    image: pierson07/immich_notify:latest
    container_name: immich_notify
    env_file:
      - stack.env
    volumes:
      - /path/to/data.txt:/path/to/data.txt # optional, use to retain data through redeployment
    ports:
      - 5000:5000
    restart: unless-stopped
    
  ntfy:
    image: binwiederhier/ntfy
    container_name: ntfy
    command:
      - serve
    volumes:
      - /var/cache/ntfy:/var/cache/ntfy
      - /etc/ntfy:/etc/ntfy
    ports:
      - 80:80
    healthcheck: # optional: remember to adapt the host:port to your environment
        test: ["CMD-SHELL", "wget -q --tries=1 http://localhost:80/v1/health -O - | grep -Eo '\"healthy\"\\s*:\\s*true' || exit 1"]
        interval: 60s
        timeout: 10s
        retries: 3
        start_period: 40s
    restart: unless-stopped
```

## stack.env
```
# Filepath to store data (recommended to use external storage for data, otherwise config and data will be lost
FILEPATH=./

# Debug flag (optional)
DEBUG=False
```

## server.yml (only needed for self hosted ntfy w/ iOS notifications)
```
# ntfy server config file
#
# Please refer to the documentation at https://ntfy.sh/docs/config/ for details.
# All options also support underscores (_) instead of dashes (-) to comply with the YAML spec.

# Public facing base URL of the service (e.g. https://ntfy.sh or https://ntfy.example.com)
#
# This setting is required for any of the following features:
# - attachments (to return a download URL)
# - e-mail sending (for the topic URL in the email footer)
# - iOS push notifications for self-hosted servers (to calculate the Firebase poll_request topic)
# - Matrix Push Gateway (to validate that the pushkey is correct)
#
base-url: <ntfy URL>

# Listen address for the HTTP & HTTPS web server. If "listen-https" is set, you must also
# set "key-file" and "cert-file". Format: [<ip>]:<port>, e.g. "1.2.3.4:8080".
#
# To listen on all interfaces, you may omit the IP address, e.g. ":443".
# To disable HTTP, set "listen-http" to "-".
#
# listen-http: ":80"
# listen-https:

# Listen on a Unix socket, e.g. /var/lib/ntfy/ntfy.sock
# This can be useful to avoid port issues on local systems, and to simplify permissions.
#
# listen-unix: <socket-path>
# listen-unix-mode: <linux permissions, e.g. 0700>

# Path to the private key & cert file for the HTTPS web server. Not used if "listen-https" is not set.
#
# key-file: <filename>
# cert-file: <filename>

# If set, also publish messages to a Firebase Cloud Messaging (FCM) topic for your app.
# This is optional and only required to save battery when using the Android app.
#
# firebase-key-file: <filename>

# If "cache-file" is set, messages are cached in a local SQLite database instead of only in-memory.
# This allows for service restarts without losing messages in support of the since= parameter.
#
# The "cache-duration" parameter defines the duration for which messages will be buffered
# before they are deleted. This is required to support the "since=..." and "poll=1" parameter.
# To disable the cache entirely (on-disk/in-memory), set "cache-duration" to 0.
# The cache file is created automatically, provided that the correct permissions are set.
#
# The "cache-startup-queries" parameter allows you to run commands when the database is initialized,
# e.g. to enable WAL mode (see https://phiresky.github.io/blog/2020/sqlite-performance-tuning/)).
# Example:
#    cache-startup-queries: |
#       pragma journal_mode = WAL;
#       pragma synchronous = normal;
#       pragma temp_store = memory;
#       pragma busy_timeout = 15000;
#       vacuum;
#
# The "cache-batch-size" and "cache-batch-timeout" parameter allow enabling async batch writing
# of messages. If set, messages will be queued and written to the database in batches of the given
# size, or after the given timeout. This is only required for high volume servers.
#
# Debian/RPM package users:
#   Use /var/cache/ntfy/cache.db as cache file to avoid permission issues. The package
#   creates this folder for you.
#
# Check your permissions:
#   If you are running ntfy with systemd, make sure this cache file is owned by the
#   ntfy user and group by running: chown ntfy.ntfy <filename>.
#
# cache-file: <filename>
# cache-duration: "12h"
# cache-startup-queries:
# cache-batch-size: 0
# cache-batch-timeout: "0ms"

# If set, access to the ntfy server and API can be controlled on a granular level using
# the 'ntfy user' and 'ntfy access' commands. See the --help pages for details, or check the docs.
#
# - auth-file is the SQLite user/access database; it is created automatically if it doesn't already exist
# - auth-default-access defines the default/fallback access if no access control entry is found; it can be
#   set to "read-write" (default), "read-only", "write-only" or "deny-all".
# - auth-startup-queries allows you to run commands when the database is initialized, e.g. to enable
#   WAL mode. This is similar to cache-startup-queries. See above for details.
#
# Debian/RPM package users:
#   Use /var/lib/ntfy/user.db as user database to avoid permission issues. The package
#   creates this folder for you.
#
# Check your permissions:
#   If you are running ntfy with systemd, make sure this user database file is owned by the
#   ntfy user and group by running: chown ntfy.ntfy <filename>.
#
# auth-file: <filename>
# auth-default-access: "read-write"
# auth-startup-queries:

# If set, the X-Forwarded-For header is used to determine the visitor IP address
# instead of the remote address of the connection.
#
# WARNING: If you are behind a proxy, you must set this, otherwise all visitors are rate limited
#          as if they are one.
#
# behind-proxy: false

# If enabled, clients can attach files to notifications as attachments. Minimum settings to enable attachments
# are "attachment-cache-dir" and "base-url".
#
# - attachment-cache-dir is the cache directory for attached files
# - attachment-total-size-limit is the limit of the on-disk attachment cache directory (total size)
# - attachment-file-size-limit is the per-file attachment size limit (e.g. 300k, 2M, 100M)
# - attachment-expiry-duration is the duration after which uploaded attachments will be deleted (e.g. 3h, 20h)
#
# attachment-cache-dir:
# attachment-total-size-limit: "5G"
# attachment-file-size-limit: "15M"
# attachment-expiry-duration: "3h"

# If enabled, allow outgoing e-mail notifications via the 'X-Email' header. If this header is set,
# messages will additionally be sent out as e-mail using an external SMTP server.
#
# As of today, only SMTP servers with plain text auth (or no auth at all), and STARTLS are supported.
# Please also refer to the rate limiting settings below (visitor-email-limit-burst & visitor-email-limit-burst).
#
# - smtp-sender-addr is the hostname:port of the SMTP server
# - smtp-sender-from is the e-mail address of the sender
# - smtp-sender-user/smtp-sender-pass are the username and password of the SMTP user (leave blank for no auth)
#
# smtp-sender-addr:
# smtp-sender-from:
# smtp-sender-user:
# smtp-sender-pass:

# If enabled, ntfy will launch a lightweight SMTP server for incoming messages. Once configured, users can send
# emails to a topic e-mail address to publish messages to a topic.
#
# - smtp-server-listen defines the IP address and port the SMTP server will listen on, e.g. :25 or 1.2.3.4:25
# - smtp-server-domain is the e-mail domain, e.g. ntfy.sh
# - smtp-server-addr-prefix is an optional prefix for the e-mail addresses to prevent spam. If set to "ntfy-",
#   for instance, only e-mails to ntfy-$topic@ntfy.sh will be accepted. If this is not set, all emails to
#   $topic@ntfy.sh will be accepted (which may obviously be a spam problem).
#
# smtp-server-listen:
# smtp-server-domain:
# smtp-server-addr-prefix:

# If enabled, ntfy can perform voice calls via Twilio via the "X-Call" header.
#
# - twilio-account is the Twilio account SID, e.g. AC12345beefbeef67890beefbeef122586
# - twilio-auth-token is the Twilio auth token, e.g. affebeef258625862586258625862586
# - twilio-phone-number is the outgoing phone number you purchased, e.g. +18775132586
# - twilio-verify-service is the Twilio Verify service SID, e.g. VA12345beefbeef67890beefbeef122586
#
# twilio-account:
# twilio-auth-token:
# twilio-phone-number:
# twilio-verify-service:

# Interval in which keepalive messages are sent to the client. This is to prevent
# intermediaries closing the connection for inactivity.
#
# Note that the Android app has a hardcoded timeout at 77s, so it should be less than that.
#
# keepalive-interval: "45s"

# Interval in which the manager prunes old messages, deletes topics
# and prints the stats.
#
# manager-interval: "1m"

# Defines topic names that are not allowed, because they are otherwise used. There are a few default topics
# that cannot be used (e.g. app, account, settings, ...). To extend the default list, define them here.
#
# Example:
#   disallowed-topics:
#     - about
#     - pricing
#     - contact
#
# disallowed-topics:

# Defines the root path of the web app, or disables the web app entirely.
#
# Can be any simple path, e.g. "/", "/app", or "/ntfy". For backwards-compatibility reasons,
# the values "app" (maps to "/"), "home" (maps to "/app"), or "disable" (maps to "") to disable
# the web app entirely.
#
# web-root: /

# Various feature flags used to control the web app, and API access, mainly around user and
# account management.
#
# - enable-signup allows users to sign up via the web app, or API
# - enable-login allows users to log in via the web app, or API
# - enable-reservations allows users to reserve topics (if their tier allows it)
#
# enable-signup: false
# enable-login: false
# enable-reservations: false

# Server URL of a Firebase/APNS-connected ntfy server (likely "https://ntfy.sh").
#
# iOS users:
#   If you use the iOS ntfy app, you MUST configure this to receive timely notifications. You'll like want this: 
#  upstream-base-url: "https://ntfy.sh"
#
# If set, all incoming messages will publish a "poll_request" message to the configured upstream server, containing
# the message ID of the original message, instructing the iOS app to poll this server for the actual message contents.
# This is to prevent the upstream server and Firebase/APNS from being able to read the message.
#
# - upstream-base-url is the base URL of the upstream server. Should be "https://ntfy.sh".
# - upstream-access-token is the token used to authenticate with the upstream server. This is only required
#   if you exceed the upstream rate limits, or the uptream server requires authentication.
#
upstream-base-url: "https://ntfy.sh"
# upstream-access-token:

# Rate limiting: Total number of topics before the server rejects new topics.
#
# global-topic-limit: 15000

# Rate limiting: Number of subscriptions per visitor (IP address)
#
# visitor-subscription-limit: 30

# Rate limiting: Allowed GET/PUT/POST requests per second, per visitor:
# - visitor-request-limit-burst is the initial bucket of requests each visitor has
# - visitor-request-limit-replenish is the rate at which the bucket is refilled
# - visitor-request-limit-exempt-hosts is a comma-separated list of hostnames, IPs or CIDRs to be
#   exempt from request rate limiting. Hostnames are resolved at the time the server is started.
#   Example: "1.2.3.4,ntfy.example.com,8.7.6.0/24"
#
# visitor-request-limit-burst: 60
# visitor-request-limit-replenish: "5s"
# visitor-request-limit-exempt-hosts: ""

# Rate limiting: Hard daily limit of messages per visitor and day. The limit is reset
# every day at midnight UTC. If the limit is not set (or set to zero), the request
# limit (see above) governs the upper limit.
#
# visitor-message-daily-limit: 0

# Rate limiting: Allowed emails per visitor:
# - visitor-email-limit-burst is the initial bucket of emails each visitor has
# - visitor-email-limit-replenish is the rate at which the bucket is refilled
#
# visitor-email-limit-burst: 16
# visitor-email-limit-replenish: "1h"

# Rate limiting: Attachment size and bandwidth limits per visitor:
# - visitor-attachment-total-size-limit is the total storage limit used for attachments per visitor
# - visitor-attachment-daily-bandwidth-limit is the total daily attachment download/upload traffic limit per visitor
#
# visitor-attachment-total-size-limit: "100M"
# visitor-attachment-daily-bandwidth-limit: "500M"

# Rate limiting: Enable subscriber-based rate limiting (mostly used for UnifiedPush)
#
# If enabled, subscribers may opt to have published messages counted against their own rate limits, as opposed
# to the publisher's rate limits. This is especially useful to increase the amount of messages that high-volume
# publishers (e.g. Matrix/Mastodon servers) are allowed to send.
#
# Once enabled, a client may send a "Rate-Topics: <topic1>,<topic2>,..." header when subscribing to topics via
# HTTP stream, or websockets, thereby registering itself as the "rate visitor", i.e. the visitor whose rate limits
# to use when publishing on this topic. Note: Setting the rate visitor requires READ-WRITE permission on the topic.
#
# UnifiedPush only: If this setting is enabled, publishing to UnifiedPush topics will lead to a HTTP 507 response if
# no "rate visitor" has been previously registered. This is to avoid burning the publisher's "visitor-message-daily-limit".
#
# visitor-subscriber-rate-limiting: false

# Payments integration via Stripe
#
# - stripe-secret-key is the key used for the Stripe API communication. Setting this values
#   enables payments in the ntfy web app (e.g. Upgrade dialog). See https://dashboard.stripe.com/apikeys.
# - stripe-webhook-key is the key required to validate the authenticity of incoming webhooks from Stripe.
#   Webhooks are essential up keep the local database in sync with the payment provider. See https://dashboard.stripe.com/webhooks.
# - billing-contact is an email address or website displayed in the "Upgrade tier" dialog to let people reach
#   out with billing questions. If unset, nothing will be displayed.
#
# stripe-secret-key:
# stripe-webhook-key:
# billing-contact:

# Metrics
#
# ntfy can expose Prometheus-style metrics via a /metrics endpoint, or on a dedicated listen IP/port.
# Metrics may be considered sensitive information, so before you enable them, be sure you know what you are
# doing, and/or secure access to the endpoint in your reverse proxy.
#
# - enable-metrics enables the /metrics endpoint for the default ntfy server (i.e. HTTP, HTTPS and/or Unix socket)
# - metrics-listen-http exposes the metrics endpoint via a dedicated [IP]:port. If set, this option implicitly
#   enables metrics as well, e.g. "10.0.1.1:9090" or ":9090"
#
# enable-metrics: false
# metrics-listen-http:

# Profiling
#
# ntfy can expose Go's net/http/pprof endpoints to support profiling of the ntfy server. If enabled, ntfy will listen
# on a dedicated listen IP/port, which can be accessed via the web browser on http://<ip>:<port>/debug/pprof/.
# This can be helpful to expose bottlenecks, and visualize call flows. See https://pkg.go.dev/net/http/pprof for details.
#
# profile-listen-http:

# Logging options
#
# By default, ntfy logs to the console (stderr), with an "info" log level, and in a human-readable text format.
# ntfy supports five different log levels, can also write to a file, log as JSON, and even supports granular
# log level overrides for easier debugging. Some options (log-level and log-level-overrides) can be hot reloaded
# by calling "kill -HUP $pid" or "systemctl reload ntfy".
#
# - log-format defines the output format, can be "text" (default) or "json"
# - log-file is a filename to write logs to. If this is not set, ntfy logs to stderr.
# - log-level defines the default log level, can be one of "trace", "debug", "info" (default), "warn" or "error".
#   Be aware that "debug" (and particularly "trace") can be VERY CHATTY. Only turn them on briefly for debugging purposes.
# - log-level-overrides lets you override the log level if certain fields match. This is incredibly powerful
#   for debugging certain parts of the system (e.g. only the account management, or only a certain visitor).
#   This is an array of strings in the format:
#      - "field=value -> level" to match a value exactly, e.g. "tag=manager -> trace"
#      - "field -> level" to match any value, e.g. "time_taken_ms -> debug"
#   Warning: Using log-level-overrides has a performance penalty. Only use it for temporary debugging.
#
# Example (good for production):
#   log-level: info
#   log-format: json
#   log-file: /var/log/ntfy.log
#
# Example level overrides (for debugging, only use temporarily):
#   log-level-overrides:
#      - "tag=manager -> trace"
#      - "visitor_ip=1.2.3.4 -> debug"
#      - "time_taken_ms -> debug"
#
# log-level: info
# log-level-overrides:
# log-format: text
# log-file:
```
