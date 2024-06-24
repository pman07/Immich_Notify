import os
import ast
import socket
import requests
import schedule
import time
import json
from urllib.parse import urlparse
from flask import Flask, redirect, render_template, request


FILE_PATH = os.environ.get('FILEPATH', './')
DEBUG = (os.environ.get('DEBUG', False) == 'True')

default_config = {
    "Immich Local URL": "http://192.168.1.1:2283",
    "Immich External URL": "https://immich.com",
    "Immich API Key": "abc123",
    "ntfy URL": "http://192.168.1.1:8080",
    "ntfy Icon URL": "https://raw.githubusercontent.com/immich-app/immich/main/design/immich-logo.png",
    "ntfy Email": "fake@gmail.com",
    "ntfy Email Tag": "",
    "ntfy Authorization": ""
}

default_app = {
    "ENABLE_NOTIFICATIONS": False,
    "SCHEDULE_TIME": 15
}


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


def get_albums(config, saved):
    list = []
    base_url = config["Immich Local URL"]
    api_key = config["Immich API Key"]

    url = base_url + "/api/albums?shared=true"

    payload = {}
    headers = {
        'Accept': 'application/json',
        'x-api-key': api_key
    }

    try:
        response = requests.request("GET", url, headers=headers, data=payload)

        a = response.json()
        print(a)

        if 'error' in a:
            saved = a['message']
        else:
            for album in a:
                tmp = {}
                newAlbum = True

                if (saved):
                    for savedAlbum in saved:
                        if album['id'] == savedAlbum['id']:
                            newAlbum = False

                if newAlbum:
                    tmp['id'] = album['id']
                    tmp['albumName'] = album['albumName']
                    tmp['monitored'] = False
                    tmp['topic'] = ''
                    list.append(tmp)
                    if DEBUG:
                        print(tmp['id'], tmp['albumName'])

            if len(list) > 0:
                if saved:
                    saved.append(list)
                else:
                    saved = list

    except requests.exceptions.ConnectionError as e:
        saved = e
        print('Error Getting Shared Albums', e)
    return saved


config_file_path = FILE_PATH + "config.json"
album_file_path = FILE_PATH + "album.json"
app_file_path = FILE_PATH + "app.json"

config = load_data(config_file_path, default_data=default_config)
saved_albums = load_data(album_file_path)
app_vars = load_data(app_file_path, default_data=default_app)

ENABLE_GET_ALBUMS = False
ENABLE_NOTIFICATIONS = False

app = Flask(__name__)

users_shared_albums = saved_albums
error_message = ""


@app.route('/')
def index():
    global config
    global users_shared_albums
    global ENABLE_GET_ALBUMS
    global app_vars
    global error_message

    return render_template('./config.html', config=config, albums=users_shared_albums,
                           enable_get_albums=ENABLE_GET_ALBUMS, app=app_vars, error_message=error_message)


@app.route('/update', methods=['POST'])
def update_config():

    global config
    global users_shared_albums
    global config_file_path
    global ENABLE_GET_ALBUMS

    for key in request.form:
        if DEBUG:
            print(key)
        if key in config:
            config[key] = request.form[key]

    write_data(config_file_path, config)

    return redirect('/')


@app.route('/saveAlbums', methods=['POST'])
def save_albums():

    global config
    global users_shared_albums
    global ENABLE_GET_ALBUMS
    global album_file_path

    for item in users_shared_albums:
        monitored = item['id'] + '_monitored'
        topic = item['id'] + '_topic'
        item['monitored'] = request.form.get(monitored, False) == 'on'
        if not item['monitored']:
            item['topic'] = ""
        else:
            item['topic'] = request.form.get(topic)

    write_data(album_file_path, users_shared_albums)

    return redirect('/')


@app.route('/getAlbums', methods=['POST'])
def load_albums():
    global config
    global users_shared_albums
    global ENABLE_GET_ALBUMS
    global error_message

    try:
        temp = get_albums(config, saved_albums)

        if isinstance(temp, requests.exceptions.ConnectionError):
            error_message = temp
        elif isinstance(temp, str):
            error_message = temp
        else:
            users_shared_albums = temp
            error_message = ""
            ENABLE_GET_ALBUMS = True
    except requests.exceptions.RequestException as e:
        print("Failed to fetch album data:", e)

    return redirect('/')


@app.route('/startApplication', methods=['POST'])
def start_application():
    global app_vars

    app_vars['ENABLE_NOTIFICATIONS'] = 'True'
    write_data(app_file_path, app_vars)

    return redirect('/')


@app.route('/stopApplication', methods=['POST'])
def stop_application():
    global app_vars

    app_vars['ENABLE_NOTIFICATIONS'] = 'False'
    write_data(app_file_path, app_vars)

    return redirect('/')


@app.route('/updateSchedule', methods=['POST'])
def update_schedule():

    global app_vars
    global app_file_path

    app_vars['SCHEDULE_TIME'] = str(request.form.get('Schedule_Time'))

    write_data(app_file_path, app_vars)

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0')



