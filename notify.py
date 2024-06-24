import os
import ast
import socket
import requests
import schedule
import time
import json
from urllib.parse import urlparse

FILE_PATH = os.environ.get('FILEPATH', './')
DEBUG = (os.environ.get('DEBUG', 'False') == 'True')
app_file_path = FILE_PATH + "app.json"

IMMICH_API_KEY = ""
BASE_URL = ""
EXT_URL = ""
NTFY_URL = ""
NTFY_ICON = ""
EMAIL = ""
NTFY_EMAIL_TAG = ""
AUTHORIZATION_KEY = ""


def check(host, port, timeout=1):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
    except:
        return False
    else:
        sock.close()
        return True


def load_data(path, **kwargs):
    default_data = kwargs.get('default_data')
    try:
        # Try to open the JSON file for reading
        with open(path, "r") as file:
            # Load existing configuration
            data = json.load(file)
        if DEBUG:
            print(path + " loaded successfully.")
        return data

    except FileNotFoundError:
        if default_data:
            # If the file doesn't exist, create it with default values
            if DEBUG:
                print(path + " not found. Creating a new one with default values...")
            with open(path, "w") as file:
                # Write default configuration to the file
                json.dump(default_data, file, indent=4)
            if DEBUG:
                print(path + " created with default values.")
            return default_data
        else:
            if DEBUG:
                print("No default data to write to file")
            return


def write_data(path, data):
    try:
        # Try to open the JSON file for reading
        with open(path, "w") as file:
            json.dump(data, file, indent=4)
        if DEBUG:
            print(path + " written successfully.")
    except IOError:
        print("Error writing data")


def get_album_contents(base_url, uuid, api_key):
    url = base_url + "/api/albums/" + uuid

    payload = {}
    headers = {
        'Accept': 'application/json',
        'x-api-key': api_key
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    a = response.json()

    count = a['assetCount']

    return count


def ntfy_notification(ntfy_url, ntfy_title, ntfy_message, ntfy_link, ntfy_icon, authorization=''):
    if authorization != '':
        requests.post(ntfy_url,
                      data=ntfy_message.encode('utf-8'),
                      headers={
                          "Title": ntfy_title,
                          "Click": ntfy_link,
                          "Icon": ntfy_icon,
                          "Authorization": "Basic " + authorization
                      })
    else:
        requests.post(ntfy_url,
                      data=ntfy_message.encode('utf-8'),
                      headers={
                          "Title": ntfy_title,
                          "Click": ntfy_link,
                          "Icon": ntfy_icon
                      })


def ntfy_email(ntfy_url, ntfy_message, ntfy_email, ntfy_tag, authorization=''):
    if authorization != '':
        requests.post(ntfy_url,
                      data=ntfy_message,
                      headers={
                          "Email": ntfy_email,
                          "Tags": ntfy_tag,
                          "Authorization": "Basic " + authorization
                      })
    else:
        requests.post(ntfy_url,
                      data=ntfy_message,
                      headers={
                          "Email": ntfy_email,
                          "Tags": ntfy_tag
                      })


def check_and_notify():
    monitored_albums = []
    config_file_path = FILE_PATH + 'config.json'
    data_file_path = FILE_PATH + 'data.json'
    albums_file_path = FILE_PATH + 'album.json'

    print('Immich Notifications Triggered')

    if os.path.exists(albums_file_path):
        users_shared_albums = load_data(albums_file_path)

        for item in users_shared_albums:
            if item['monitored']:
                monitored_albums.append(item)

    if os.path.exists(albums_file_path):
        config = load_data(config_file_path)
        IMMICH_API_KEY = config['Immich API Key']
        BASE_URL = config['Immich Local URL']
        EXT_URL = config['Immich External URL']
        NTFY_URL = config['ntfy URL']
        NTFY_ICON = config['ntfy Icon URL']
        EMAIL = config['ntfy Email']
        NTFY_EMAIL_TAG = config['ntfy Email Tag']
        AUTHORIZATION_KEY = config['ntfy Authorization']
        url = urlparse(BASE_URL)

    if check(url.hostname, url.port):
        if os.path.exists(data_file_path):
            if DEBUG:
                print('File Exists')
            stored_albums = load_data(data_file_path)
            if DEBUG:
                for item in stored_albums:
                    print('Items:', item['stored items'])

            for a in monitored_albums:
                new_album = True
                tmp_album = a
                for b in stored_albums:
                    if a['id'] == b['id']:
                        new_album = False
                        if a['topic'] != b['topic']:
                            b['topic'] = a['topic']
                            print('Updated topic for ', b['albumName'])

                if new_album:
                    stored_albums.append(tmp_album)
                    print('Started monitoring ', a['albumName'])

            updated_stored_albums = []
            for a in stored_albums:
                monitored = False
                for b in monitored_albums:
                    if a['id'] == b['id']:
                        monitored = True
                        updated_stored_albums.append(a)

                if not monitored:
                    print('Stopped monitoring ', a['albumName'])
                    continue

                album_id = a['id']
                topic = a['topic']
                if DEBUG:
                    print("Topic: ", topic)
                    print("Album ID: ", album_id)
                total_items = get_album_contents(BASE_URL, album_id, IMMICH_API_KEY)

                if 'stored items' not in a:
                    a['stored items'] = total_items

                if DEBUG:
                    print('Album Name: ', a['albumName'])
                    print('Total Items Stored: ', a['stored items'])
                    print('Total Items Now: ', total_items)

                new_items = total_items - a['stored items']

                a['stored items'] = total_items

                if DEBUG:
                    print('Album Name:', a['albumName'])
                    print("Items Added:", new_items)

                if new_items > 0:
                    topic = a['topic']
                    url = NTFY_URL + '/' + topic
                    title = 'Immich'
                    link = EXT_URL + '/albums/' + a['id']

                    if new_items > 1:
                        message = str(new_items) + ' photos added to ' + a['albumName'] + '!'
                    else:
                        message = 'Photo added to ' + a['albumName'] + '!'

                    ntfy_notification(url, title, message, link, NTFY_ICON, AUTHORIZATION_KEY)

                    if EMAIL != '':
                        topic = a['topic'] + '_email'
                        url = NTFY_URL + '/' + topic
                        message = 'Immich - ' + message + ' ' + link

                        ntfy_email(url, message, EMAIL, NTFY_EMAIL_TAG, AUTHORIZATION_KEY)

            stored_albums = updated_stored_albums

        else:
            for key in monitored_albums:
                album_id = key['id']
                total_items = get_album_contents(BASE_URL, album_id, IMMICH_API_KEY)
                key['stored items'] = total_items

                if DEBUG:
                    print('Album Name:', key['albumName'])
                    print('Total Items Now: ', total_items)

            stored_albums = monitored_albums

        write_data(data_file_path, stored_albums)


stored_time = "0"
stored_enable = ''

while True:
    if os.path.exists(app_file_path):
        app_vars = load_data(app_file_path)
        ENABLE_NOTIFICATIONS = app_vars['ENABLE_NOTIFICATIONS'] == 'True'
        SCHEDULE_TIME = app_vars["SCHEDULE_TIME"]

        if SCHEDULE_TIME != stored_time:
            print("Schedule Time: ", SCHEDULE_TIME, " Minutes")
            schedule.cancel_job(check_and_notify)
            schedule.every(int(SCHEDULE_TIME)).minutes.do(check_and_notify)
        if ENABLE_NOTIFICATIONS != stored_enable:
            print("Enable Notifications: ", ENABLE_NOTIFICATIONS)
        if ENABLE_NOTIFICATIONS:
            schedule.run_pending()
        stored_enable = ENABLE_NOTIFICATIONS
        stored_time = SCHEDULE_TIME
    else:
        print('No App Config JSON file at ', app_file_path)
    time.sleep(1)
