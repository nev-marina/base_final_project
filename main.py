import datetime
import requests
from tqdm import tqdm
import sys
import json
import time

with open('token_vk.txt', 'r') as file_object:
    token_vk = file_object.read().strip()

with open('token_ya.txt', 'r') as file_object:
    token_ya = file_object.read().strip()


class VkApi:

    def __init__(self, token, user_id, version='5.131'):
        self.url = 'https://api.vk.com/method/'
        self.version = version
        self.params = {'access_token': token, 'v': self.version}
        self.user_id = user_id

    def get_user(self):
        user_url = self.url+'users.get'
        user_params = {'user_ids': self.user_id}
        user = requests.get(user_url, params={**self.params, **user_params}).json()
        if user.get('error') is None:
            if len(user['response']) != 0:
                user_id = user['response'][0]['id']
            else:
                print(f'Пользователь "{self.user_id}" не найден!')
                sys.exit()
        else:
            print(f'Некорректный ввод!')
            sys.exit()
        return user_id

    def get_photos(self):
        user_id = self.get_user()
        get_photo_url = self.url+'photos.get'
        get_photo_params = {'user_id': user_id, 'extended': '1',
                            'album_id': 'profile', 'count': count, 'photo_sizes': '1'}
        req = requests.get(get_photo_url, params={**self.params, **get_photo_params}).json()
        return req['response']['items']

    def get_name_file(self):
        photos_ = []
        list_photos = []
        like = []
        photos = self.get_photos()
        for photo in photos:
            photo_date = (datetime.datetime.fromtimestamp(photo['date'])).strftime('%d-%m-%Y')
            photo_likes = photo['likes']['count']
            photo_url = photo['sizes'][len(photo['sizes'])-1]['url']
            photo_size = photo['sizes'][len(photo['sizes'])-1]['type']
            if photo_likes not in like:
                photos_.append({'Name': str(photo_likes)+'.jpg', 'Likes': str(photo_likes), 'Date': photo_date,
                                'Url': photo_url, 'Size type': photo_size})
                list_photos.append({"file_name": str(photo_likes)+'.jpg', "size": photo_size})
            else:
                photos_.append(
                    {'Name': str(photo_likes)+"_"+photo_date+'.jpg', 'Likes': str(photo_likes), 'Date': photo_date,
                     'Url': photo_url, 'Size type': photo_size})
                list_photos.append({"file_name": str(photo_likes)+"_"+photo_date+'.jpg', "size": photo_size})
            like.append(photo_likes)
            with open('log.json', 'w') as f:
                json.dump(list_photos, f, indent=2, ensure_ascii=False)
        return photos_


class YandexDisk:

    def __init__(self, token, folder):
        self.token = token
        self.folder = folder
        self.url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json',
                        'Authorization': f'OAuth {token_ya}'}

    def create_folder(self, folder):
        self.folder = folder
        requests.put(self.url, headers=self.headers, params={'path': f"/{self.folder}"})
        return

    def upload_to_yandex(self):
        self.create_folder(self.folder)
        name_list = []
        vk_list = Vk.get_name_file()
        for photo in tqdm(vk_list, desc='Загрузка', unit='photo', colour='green'):
            time.sleep(1)
            name = str(photo['Name'])
            name_list.append(name)
            requests.post(self.url+'/upload', headers=self.headers,
                          params={'url': photo['Url'], 'path': f"/{self.folder}/"+name})
        print(f' Загружено {len(vk_list)} фото')
        return


if __name__ == '__main__':
    user_name = input("Введите id или username: ")
    count = int(input("Введите количество фотографий для копирования: "))
    yandex_directory = input("Введите имя каталога для Яндекс.Диск: ")

    Vk = VkApi(token_vk, user_name)
    Yandex = YandexDisk(token_ya, yandex_directory)
    Yandex.upload_to_yandex()
