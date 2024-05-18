import os
import sys
import requests
import json
# from pprint import pprint
import vk_token
import ya_poligon_token
vk_token = vk_token.access()
ya_token = ya_poligon_token.access()

# Словарь параметров по умолчанию для ВК
input_param = {'count': 5, 'album_id': 'profile', 'rev': 1}
while 1:
    ''' распределяем параметры по словарю
    если ошибки, выдаем повторный запрос ввода '''

    print('Введите user_id вконтакте (обязательный параметр)')
    print('Дополнительно можно ввести, через пробел, в одну строку')
    print('Первый указаный в примере параметр == параметр по умолчанию')
    print(f'id(только цифры, либо строковый алиас) '
          f'count=(5, колличество копируемых фото) '
          f'album_id=(profile или wall) '
          f'(другие параметры album_id пока не поддерживаются)'
          f'rev=(1 или 0, 0-хронологический, 1-обратный)')
    print('Вводить только значения либо число, либо строка')
    id_and_param = list(input().split())
    id = id_and_param.pop(0)
    print(id_and_param)
    if len(id_and_param) < 1 or len(id_and_param) > 3:
        break
    for i in range(len(id_and_param)):
        if (i == 0) and id_and_param[i].isdigit():
            input_param['count'] = id_and_param[i]
        elif (i == 1) and id_and_param[i].isalpha():
            input_param['album_id'] = id_and_param[i]
        elif (i == 2) and id_and_param[i] in '01':
            input_param['rev'] = id_and_param[i]
        else:
            if i == 0:
                print('Неверное значение count')
            elif i == 1:
                print('Неверное значение album_id')
            elif i == 2:
                print('Неверное значение rev')


# print('Введите Яндекс Полигон OAuth-токен')
# ya_token = input()
# print(access_token)
print(input_param)


class VK:
    ''' Класс для работы с сайтом vk.ru'''
    photo_size = 'wzyrqpoxms'

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
            return id
        except IndexError:
            print('Похоже данный id не существует')
            print('Restarting...')
            # Данная перезагрузка подойдет для Linux и Mac
            os.execv(sys.executable, ['python3'] + sys.argv)
        except KeyError:
            print('Такая вот вышла ошибочка')
            print(response.json()['error']['error_msg'])

    def photos_get(self, count=5, album_id='profile', rev=1):
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
        with open('photos.json', 'wt', encoding='utf-8') as outf:
            json.dump(self.photos_get(), outf)

    id = property(get_id, set_id)


class YaDi:
    ''' Класс для работы с Яндекс Диском '''

    def __init__(self, ya_token):
        self.token = ya_token


class WorkJson:
    pass


vk = VK(vk_token, id)
# print(vk.user_info())
# print(vk.id)
vk.photos_json()
# pprint(vk.photos_get())
# # print(vk.user_get_id())
# os.remove('photos.json')
