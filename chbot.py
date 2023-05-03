import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
from datetime import date

with open('tokens.txt') as file_object:
    user_token = file_object.readline().strip()
    comm_token = file_object.readline().strip()


class BotVK:
    def __init__(self):
        self.comm_token = comm_token
        self.vk = vk_api.VkApi(token=self.comm_token)
        self.longpoll = VkLongPoll(self.vk)

    def send_msg(self, user_id, message):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'message': message,
                                         'random_id': randrange(10 ** 7)})

    def send_photo(self, user_id, user_vk_id, photo_id):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'attachment': f'photo{user_vk_id}_{photo_id}',
                                         'random_id': randrange(10 ** 7)})

    def send_but(self, user_id, message, keyboard=None):
        post = {'user_id': user_id,
                'message': message,
                'random_id': randrange(10 ** 7)
                }
        if keyboard != None:
            post['keyboard'] = keyboard.get_keyboard()
        else:
            post = post
        self.vk.method('messages.send', post)

class UsersVK:
    def __init__(self):
        self.user_token = user_token
        self.vk = vk_api.VkApi(token=self.user_token)
        self.url = 'https://api.vk.com/method/'
        self.params = {'access_token': self.user_token,
                       'v': '5.131'
                       }

    def get_name(self, user_id):
        params = {'user_ids': user_id,
                  'fields': 'bdate'
                  }
        resp = self.vk.method('users.get', {**self.params, **params})
        try:
            first_name = resp[0]['first_name']
            return first_name
        except Exception:
            return '''произошла ошибка, возможно не получится продолжить поиск, 
                      мы работаем над этим, чуть позже все обязательно получится'''

    def get_sex(self, user_id):
        params = {'user_ids': user_id,
                  'fields': 'sex'
                  }
        resp = self.vk.method('users.get', {**self.params, **params})
        try:
            if resp[0]['sex'] == 2:
                search_sex = 1
                return search_sex
            elif resp[0]['sex'] == 1:
                search_sex = 2
                return search_sex
            elif resp[0]['sex'] == 0:
                bot.send_msg(user_id, 'Введите пол человека, которго ищете: 1 (если пол женский), 2 (если мужской)')
                for event in bot.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        if event.text == '1' or '2':
                            search_sex = int(event.text)
                            return search_sex
        except Exception:
            bot.send_msg(user_id, '''произошла ошибка, возможно не получится продолжить поиск, 
                                     мы работаем над этим, чуть позже все обязательно получится''')

    def get_age(self, user_id):
        params = {'user_ids': user_id,
                  'fields': 'bdate'
                  }
        resp = self.vk.method('users.get', {**self.params, **params})
        if 'bdate' in resp[0] and len(resp[0]['bdate'].split('.')) == 3:
            birth_date = resp[0]['bdate'].split('.')
            birth_year = int(birth_date[2])
            now_year = date.today().year
            age = now_year - birth_year
            return str(age)
        else:
            bot.send_msg(user_id, 'Введите возраст человека, которого ищете (например 30)): ')
            for event in bot.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    age = event.text
                    return age

    def search_town_id(self, q):
        params = {'q': q}
        resp = self.vk.method('database.getCities', {**self.params, **params})
        if resp['items']:
            return resp['items'][0]['id']
        else:
            return 1


    def get_city(self, user_id):
        params = {'user_ids': user_id,
                  'fields': 'city',
                  }
        resp = self.vk.method('users.get', {**self.params, **params})
        try:
            if 'city' in resp[0]:
                town_id = resp[0]['city']['id']
                return town_id
            else:
                bot.send_msg(user_id, 'Введите название города для поиска')
                for event in bot.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        town = event.text
                        if 3 <= len(town) <= 15:
                            return self.search_town_id(town)
                        elif len(town) > 15:
                            town = town[:15]
                            return self.search_town_id(town)
                        elif len(town) < 3:
                            bot.send_msg(user_id, '''Город не найден, для корректного поиска 
                                                     укажите ваш город в настройках вашего профиля.
                                                     А пока поиск произведен по городу Москва''')
                            return 1
        except Exception:
            bot.send_msg(user_id, '''произошла ошибка, возможно не получится продолжить поиск, 
                                     мы работаем над этим, чуть позже все обязательно получится''')

    def get_photo(self, profile_id, user_id):
        params = {'owner_id': profile_id,
                  'album_id': 'profile',
                  'extended': 'likes, comments'
                  }
        resp = self.vk.method('photos.get', {**self.params, **params})
        photos_list = []
        try:
            for item_photo in resp['items']:
                photo_id = item_photo['id']
                sum_likes_comments = item_photo['likes']['count'] + item_photo['comments']['count']
                photos_list.append((photo_id, sum_likes_comments))
            sorted_tuple = sorted(photos_list, key=lambda x: x[1], reverse=True)
            return sorted_tuple[:3]
        except Exception:
            bot.send_msg(user_id, '''произошла ошибка, возможно не получится продолжить поиск, 
                                     мы работаем над этим, чуть позже все обязательно получится''')

    def search_user(self, user_id):
        params = {'sex': self.get_sex(user_id),
                  'age_from': self.get_age(user_id),
                  'age_to': self.get_age(user_id),
                  'city': self.get_city(user_id),
                  'fields': 'relation',
                  'count': 1000}
        resp = self.vk.method('users.search', {**self.params, **params})
        try:
            profiles = resp['items']
            users_vk_id = []
            for profile in profiles:
                if profile['is_closed'] == False:
                    users_vk_id.append(profile['id'])
            return users_vk_id
        except Exception:
            bot.send_msg(user_id, '''произошла ошибка, возможно не получится продолжить поиск, 
                                     мы работаем над этим, чуть позже все обязательно получится''')

bot = BotVK()
user_vk = UsersVK()