import vk_api

from vk_api.utils import get_random_id
from user import User
from database import Database
from hackerrank import Hackerrank

# TODO: Implement lazy loading data from VK & Hackerrank replacing it with loading from the database


def init_info_chat(func):
    def init(*args):
        if args[0].chat is None:
            args[0].chat = args[0].get_info_warns_user()
            args[0].warns_user = args[0].chat['users_warn']
        func(args[0], args[1])
    return init


class Chat(object):
    def __init__(self, vk, chat_id):
        self.vk = vk
        self.id = chat_id
        self.peer_id = chat_id + 2000000000

        self.database = Database()
        self.hackerrank = Hackerrank()

        self.chat = None
        self.warns_user = None

        self.members = self.get_info_members()

        # * MARK: In the future
        # self.admins_id = self.chat['admins_id']
        # self.members_id = self.chat['members_id']

        # self.members = self.chat['members']
        # self.admins = self.chat['admins']

    def send_message(self, message):
        self.vk.messages.send(chat_id=self.id,
                              message=message,
                              random_id=get_random_id())

    def help_user(self):
        """ 
            Send a help to the certain chat
        """

        message = 'Команды пользователя:\n\
            !nemezida - Узнать, что такое Nemezida\n\
            !hackerrank "language" - Получить задачу с Hackerrank по указанному тобой языку\n\
            !hackerrank_help - Узнать доступные языки\n\
            !warns - Узнать свое количество предупреждений\n\
            !help - Моя справка'
        self.send_message(message)

    def help_admin(self):
        """ 
            Send a help to the certain chat
        """

        message = 'Команды админа:\n\
            !ban @user_id - Забанить\n\
            !warn @user_id - Выдать предупреждение\n\
            !unwarn @user_id - Откатить предупреждение\n'
        self.send_message(message)

    def hackerrank_help(self):
        """ 
            Send a possible list of languages in which you can get a task
        """

        message = 'Доступные языки: \n'
        for key in self.hackerrank.langs:
            message += f'• {key}\n'
        self.send_message(message)

    def nemezida(self):
        """ 
            Send a help about what nemezida is

            Parameters
            ----------
            chat_id : int
        """

        message = 'В древнегреческой мифологии - богиня возмездия, карающая за нарушение общественных и моральных норм. Изображалась с атрибутами контроля (весы, уздечка), наказания (меч или плеть) и быстроты (крылья, колесница, запряженная грифонами); синоним неизбежной кары. \n\
            Более подробно: https://ru.wikipedia.org/wiki/%D0%9D%D0%B5%D0%BC%D0%B5%D0%B7%D0%B8%D0%B4%D0%B0'
        self.send_message(message)

    def unknown_command(self):
        self.send_message(
            'Неизвестная команда o_O\n Воспользуйтесь командой !help')

    def get_task(self, lang):
        """
            Send a task from hackerrank in the defined language

            Parameters
            ----------
            lang : str
        """

        formatted_lang = lang.lower()

        if not formatted_lang in self.hackerrank.langs:
            self.send_message('Данного языка нет в базе!')
        else:
            name_task, difficulty_task, url_task, task = self.hackerrank.get_task(
                formatted_lang)
            message = f'Название задачи: {name_task}\n\
                Язык программирования: {lang}\n\
                Ссылка на задачу: {url_task}\n\
                Уровень сложности: {difficulty_task}\n\n{task}'
            self.send_message(message)

    @init_info_chat
    def warn_user(self, user):
        """ 
            Give a warn an user by id

            Parameters
            ----------
            user : User
        """

        str_user_id = str(user.id)

        if not str_user_id in self.warns_user:
            self.warns_user[str_user_id] = 0

        self.warns_user[str_user_id] += 1
        self.chat['users_warn'] = self.warns_user

        self.update_users_data(self.chat)
        user.warn_user()

    @init_info_chat
    def unwarn_user(self, user):
        """ 
            Take a warn back from an user by id

            Parameters
            ----------
            user : User
        """

        str_user_id = str(user.id)

        if str_user_id in self.warns_user:
            self.warns_user[str_user_id] -= 1

            self.chat['users_warn'] = self.warns_user
            self.update_users_data(self.chat)
        user.unwarn_user()

    def update_users_data(self, data):
        self.database.updateChatDocument(str(self.id), data)

    def get_info_user(self, user_id):
        warns = 0
        if not self.warns_user is None:
            if str(user_id) in self.warns_user:
                warns = self.warns_user[str(user_id)]
        return User(self.vk, user_id, self.id, warns)

    def get_info_warns_user(self):
        data = self.database.getChatDocument(str(self.id))

        if data is None:
            newData = {'users_warn': {}}
            self.database.updateChatDocument(self.id, newData)
            data = newData

        return data

    def notice_meetup(self, name, ref):
        all_users = ''
        for member in self.members:
            all_users += '[id{id}|{name}], '.format(
                id=member[1], name=member[0])

        message = '{all}в данный момент начался митап "{name}".\n Ссылка на митап: {ref}\n Приятного просмотра :) '.format(
            all=all_users, name=name, ref=ref)

        self.send_message(message)

    def get_info_members(self):
        response = self.vk.messages.getConversationMembers(
            peer_id=self.peer_id)
        members = [(member['first_name'], str(member['id']))
                   for member in response['profiles']]
        return members
