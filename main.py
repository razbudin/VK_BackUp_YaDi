
# import yadi
import os
import sys
import requests
import json
from datetime import datetime, date
from pprint import pprint
import access
vk_token = access.vk_key()
ya_token = f'OAuth {access.ya_key()}'
''' Для запуска программы создать файл access.py
c функциями vk_key возвращающая ВК-токен
и функцию ya_key  возвращающей Я-токен
Либо просто назначить переменным в этом файле данные значения
Отключив import access'''

flag = True
while flag:
    ''' распределяем параметры по словарю
    если ошибки, выдаем повторный запрос ввода '''
    # Словарь параметров по умолчанию для ВК
    input_param = {'count': 5, 'album_id': 'profile', 'rev': 1}

    print('Введите user_id вконтакте (обязательный параметр) '
          'В виде алиаса string, или число int')
    id = input()
    print('Дополнительно можно ввести, через пробел, в одну строку')
    print('Первый указаный в примере параметр == параметр по умолчанию')
    print(f'count=(5, колличество копируемых фото)\n'
          f'album_id=(profile или wall '
          f'другие параметры album_id пока не поддерживаются)\n'
          f'rev=(1 или 0, 0-хронологический, 1-обратный)')
    print('Вводить только значения число, либо строка. '
          'Или просто нажмите Enter')
    print('Пример:\n10 wall 0')
    id_and_param = list(input().split())
    # id = id_and_param.pop(0)
    if len(id_and_param) < 1 or len(id_and_param) > 3:
        break
    for i in range(len(id_and_param)):
        if (i == 0) and id_and_param[i].isdigit():
            input_param['count'] = id_and_param[i]
            flag = False
        elif (i == 1) and id_and_param[i].lower() in ['profile', 'wall']:
            input_param['album_id'] = id_and_param[i]
            flag = False
        elif (i == 2) and id_and_param[i] in '01':
            input_param['rev'] = id_and_param[i]
            flag = False
        else:
            if i == 0:
                print('Неверное значение count')
                flag = True
            elif i == 1:
                print('Неверное значение album_id')
                flag = True
            elif i == 2:
                print('Неверное значение rev')
                flag = True


class Reboot:
    '''Перезагрузка скрипта'''

    def reboot(self):
        print('Хотите перезапустить программу y/n')
        if input() == 'y':
            print('Restarting...')
            # Данная перезагрузка подойдет для Linux и Mac
            os.execv(sys.executable, ['python3'] + sys.argv)
        else:
            exit()


re = Reboot()


class VK:
    ''' Класс для работы с сайтом vk.ru'''

    def __init__(self, vk_token, id,
                 count=input_param['count'],
                 album_id=input_param['album_id'],
                 rev=input_param['rev'], version='5.199'):
        self.token = vk_token
        self.version = version
        self.count = count
        self.album_id = album_id
        self.rev = rev
        self.params = {'access_token': self.token, 'v': self.version}
        self.url = 'https://api.vk.com/method/'
        # передаем установку параметра id в
        # функцию set_id
        self.id = id

    def get_id(self):
        return self._id

    def set_id(self, id):
        ''' Если id числовой устанавливаем его,
        если буквенный отправляем в get_user_id()
        для получения цифрового id '''
        if id.isdigit():
            self._id = id
        else:
            self._id = self.user_get_id(id)

    def user_get_id(self, id):
        ''' получает id пользователя в числовом виде
        если id не существует перезагружаем скрипт '''
        params = {'user_ids': id}
        url = f'{self.url}users.get'
        try:
            response = requests.get(
                url, params={**self.params, **params})
            id = response.json()['response'][0]['id']
            if response.json()['response'][0]['is_closed']:
                print('Профиль приватный. Невозможно получить фото')
                re.reboot()
            return id
        except IndexError:
            print('Похоже данный id не существует')
            re.reboot()
        except KeyError:
            print('Такая вот вышла ошибочка')
            print(response.json()['error']['error_msg'])
            re.reboot()

    def photos_get(self, count, album_id, rev):
        ''' Получаем .json для дальнейшей работы с фотографиями '''
        params = {'owner_id': self._id,
                  'album_id': album_id,
                  'rev': rev,
                  'extended': 1,
                  'photo_sizes': 1,
                  'count': count}
        url = f'{self.url}photos.get'
        response = requests.get(
            url, params={**self.params, **params})
        return response.json()

    def photos_json(self, *args, **kwargs):
        '''*args, **kwargs для возможности передачи параметров 
        напрямую в photos_get.
        В данной реализации такая возможность не используется '''
        with open('photos.json', 'wt', encoding='utf-8') as outf:
            json.dump(self.photos_get(self.count,
                                      self.album_id,
                                      self.rev), outf)
        print('photos.json файл получен')
        print('Продолжаем...')

    id = property(get_id, set_id)


# Создаем обект класса ВК и запускаем формирование .json файла
vk = VK(vk_token, id)
vk.photos_json()


class WorkJson:

    def open_json(self):
        with open('photos.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        if json_data.get('error') is not None:
            print('Файл.json не содержит данных для обработки фото')
            print('Программа будет прекращена')
            re.reboot()
        return json_data

    def create_path(self):
        json_data = self.open_json()
        data_path = []
        if int(input_param['count']) > int(json_data['response']['count']):
            count = json_data['response']['count']
        else:
            count = int(input_param['count'])
        for i in range(count):
            size = json_data['response']['items'][i]['sizes'][-1]['type']
            likes = json_data['response']['items'][i]['likes']['count']
            url = json_data['response']['items'][i]['sizes'][-1]['url']
            ts = int(json_data['response']['items'][i]['date'])
            data = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')
            data_path.append({'size': size,
                              'likes': likes,
                              'url': url,
                              'data': data})
        with open('path.json', 'wt', encoding='utf-8') as f:
            json.dump(data_path, f)
        print('path.json сформирован')
        print('Продолжаем...')


wj = WorkJson()
wj.create_path()


class YaDi:
    ''' Класс для работы с Яндекс Диском '''

    def __init__(self, ya_token, path='VK_BackUp'):
        self.token = ya_token
        self.path = path
        self.url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.params = {'Authorization': self.token,
                       'Content-Type': 'application/json',
                       'Accept': 'application/json'}

    def create_folder(self, path):
        ''' Создает директорию в зависимости от того что придет в path
        вызывается из folder_status() '''
        if path == self.path:
            params = {'path': self.path}
            response = requests.put(
                self.url, headers=self.params, params=params)
            status = response.status_code
            if status == 201 or status == 409:
                print(f'Директория {self.path} создана')
                print('Продолжаем...')
            return status
        else:
            params = {'path': f'{self.path}/{date.today()}'}
            response = requests.put(
                self.url, headers=self.params, params=params)
            print(f'Директория {date.today()} создана')
            print('Продолжаем...')
            status = response.status_code
            return status


    def folder_status(self):
        ''' Проверяет создана ли директория
        вызывается из функции upload '''
        params = {'path': self.path}
        response = requests.get(
            self.url, headers=self.params, params=params)
        if 200 == response.status_code:
            print(f'Директория {self.path} существует')
            print('Продолжаем ...')
            status = response.status_code
        else:
            path = self.path
            status = self.create_folder(path)
        params = {'path': f'{self.path}/{date.today()}'}
        response = requests.get(
            self.url, headers=self.params, params=params)
        if response.status_code == 200:
            print(f'Директория {self.path}/{date.today()} существует')
            print('Продолжаем ...')
            status = response.status_code
        else:
            path = f'{self.path}/{date.today()}'
            status = self.create_folder(path)
        return status


            
 

    def file_status(self, likes=135):
        ''' Проверяет существует ли файл с именем
        переданым из функции upload '''
        params = {'path': f'{self.path}/{date.today()}/{likes}.jpg'}
        response = requests.get(
            self.url, headers=self.params, params=params)
        return response.status_code



    def upload(self):
        ''' Проверяет доступнось директорий и копирует фото на Я.Диск '''
        with open('path.json', 'rt') as f:
            path_json = json.load(f)
        status = self.folder_status()
        # status += self.folder_status()
        # print(f'278 {status}')
        # Загрузка фото на диск
        fileinfo = []
        if 200 <= status < 300:
            url = f'{self.url}/upload'
            for i in range(len(path_json)):
                size = path_json[i]['size']
                likes = path_json[i]['likes']
                url_ph = path_json[i]['url']
                data = path_json[i]['data']
                if self.file_status(likes) == 200:
                    params = {
                        'path': f'{self.path}/{date.today()}'
                                f'/{likes}{data}.jpg',
                        'url': url_ph}
                    response = requests.post(
                        url, headers=self.params, params=params)
                    resp_code = response.status_code
                    if int(resp_code) == 202:
                        print(f'фото {i+1} {likes}_{data}.jpg загружено')
                        name = f'{likes}_{data}.jpg'
                        fileinfo.append({'file_name': name,
                                         'size': size})
                else:
                    params = {
                        'path': f'{self.path}/{date.today()}'
                                f'/{likes}.jpg',
                        'url': url_ph}
                    response = requests.post(
                        url, headers=self.params, params=params)
                    resp_code = response.status_code
                    if int(resp_code) == 202:
                        print(f'фото {i+1} {likes}.jpg загружено')
                        name = f'{likes}_{data}.jpg'
                        fileinfo.append({'file_name': name,
                                         'size': size})
                        
            with open('file_info.json', 'w', encoding='utf-8') as f:
                json.dump(fileinfo, f)



ya = YaDi(ya_token)
ya.upload()
os.remove('photos.json')
os.remove('path.json')
