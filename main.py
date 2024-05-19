import os
import sys
import requests
import json
# from pprint import pprint
import access
vk_token = access.vk_key()
ya_token = access.ya_key()
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
    print(f'count=(5, колличество копируемых фото) '
          f'album_id=(profile или wall '
          f'другие параметры album_id пока не поддерживаются) '
          f'rev=(1 или 0, 0-хронологический, 1-обратный)')
    print('Вводить только значения число, либо строка. '
          'Или просто нажмите Enter')
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


# print('Введите Яндекс Полигон OAuth-токен')
# ya_token = input()
# print(access_token)
# print(input_param)
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
        # print(self._id, 'user_id photos_get')
        params = {'owner_id': self._id,
                  'album_id': album_id,
                  'rev': 1,
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

    # @staticmethod
    def create_path(self):
        json_data = self.open_json()
        data = []
        if int(input_param['count']) > int(json_data['response']['count']):
            count = json_data['response']['count']
        else:
            count = int(input_param['count'])
        for i in range(count):
            size = json_data['response']['items'][i]['sizes'][-1]['type']
            likes = json_data['response']['items'][i]['likes']['count']
            url = json_data['response']['items'][i]['sizes'][-1]['url']
            date = json_data['response']['items'][i]['date']
            data.append({'size': size,
                         'likes': likes,
                         'url': url,
                         'date': date})
        with open('path.json', 'wt', encoding='utf-8') as f:
            json.dump(data, f)
        print('path.json сформирован')


wj = WorkJson()
wj.create_path()


class YaDi:
    ''' Класс для работы с Яндекс Диском '''

    def __init__(self, ya_token):
        self.token = ya_token

    def create_folder(self, name='VK_BackUp'):
        pass

# pprint(vk.photos_get())
# # print(vk.user_get_id())
# os.remove('photos.json')
