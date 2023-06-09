import os
import ast
import socket
import requests


IMMICH_KEY = os.environ.get('IMMICHKEY')
BASE_URL = os.environ.get('BASEURL')
EXT_URL = os.environ.get('EXTERNALURL')
FILE_PATH = os.environ.get('FILEPATH')
ALBUMS = ast.literal_eval(os.environ['ALBUMS'])
NTFY_URL = os.environ.get('NTFYURL')
NTFY_ICON = os.environ.get('NTFYICON')
DEBUG = os.environ.get('DEBUG')


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


def save_data(file_path, dictionary):
    try:
        with open(file_path, 'w') as file:
            for key in dictionary:
                file.write(str(dictionary[key]['total items']) + '\n')
        if DEBUG:
            print("Data stored successfully!")
    except IOError:
        print("An error occurred while saving the file.")


def read_data(file_path):
    tmp = []
    try:
        with open(file_path, 'r') as file:
            for string in file:
                tmp.append(int(string.strip()))
        return tmp
    except IOError:
        print("An error occurred while loading the file.")


def get_album_contents(uuid, imkey):
    url = BASE_URL + "/api/album/" + uuid

    payload = {}
    headers = {
        'Accept': 'application/json',
        'x-api-key': imkey
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    a = response.json()
    print(a)
    album_name = a['albumName']
    count = a['assetCount']

    return album_name, count


def ntfy_notification(ntfyurl, ntfytitle, ntfymessage, ntfylink):
    requests.post(ntfyurl,
                  data=ntfymessage.encode('utf-8'),
                  headers={
                      "Title": ntfytitle,
                      "Click": ntfylink,
                      "Icon": NTFY_ICON
                  })


if __name__ == '__main__':

    total_items_stored = []
    albums = {}

    if check('192.168.1.80', 2283):
        if os.path.exists(FILE_PATH):
            if DEBUG:
                print('File Exists')
            total_items_stored = read_data(FILE_PATH)
            if DEBUG:
                for item in total_items_stored:
                    print('Items:', item)

            index = 0
            for key in ALBUMS:
                album = key
                topic = ALBUMS[key]
                if DEBUG:
                    print("Topic: ", topic)
                    print("Album ID: ", album)
                tmp_title, tmp_total = get_album_contents(album, IMMICH_KEY)
                albums[album] = {'topic': topic, 'title': tmp_title, 'total items': tmp_total,
                                 'stored items': total_items_stored[index]}
                index += 1

            if DEBUG:
                for album in albums:
                    print('Album Name: ', albums[album]['title'])
                    print('Total Items Stored: ', albums[album]['stored items'])
                    print('Total Items Now: ', albums[album]['total items'])

            index = 0
            for album in albums:
                albums[album]['new items'] = albums[album]['total items'] - albums[album]['stored items']
                index += 1

            if DEBUG:
                for album in albums:
                    print('Album Name:', albums[album]['title'])
                    print("Items Added:", albums[album]['new items'])

            for album in albums:
                if albums[album]['new items'] > 0:
                    topic = albums[album]['topic']
                    url = NTFY_URL + '/' + topic
                    title = 'Immich'
                    link = EXT_URL + '/albums/' + album

                    if albums[album]['new items'] > 1:
                        message = str(albums[album]['new items']) + ' photos added to ' + albums[album]['title'] + '!'
                    else:
                        message = 'Photo added to ' + albums[album]['title'] + '!'

                    ntfy_notification(url, title, message, link)

        else:
            for key in ALBUMS:
                album = key
                topic = ALBUMS[key]
                tmp_title, tmp_total = get_album_contents(album, IMMICH_KEY)
                albums[album] = {'topic': topic, 'title': tmp_title, 'total items': tmp_total}

            if DEBUG:
                for album in albums:
                    print('Album Name:', albums[album]['title'])
                    print('Total Items Now: ', albums[album]['total items'])

        save_data(FILE_PATH, albums)
