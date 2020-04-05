import vk_api
import re

from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from hackerrank import Hackerrank

from user import User
from chat import Chat


class VKBot(object):
    def __init__(self, token, group_id):
        super().__init__()

        self.token = token
        self.group_id = group_id

        self.vk_session = vk_api.VkApi(token=self.token)
        self.longpoll = VkBotLongPoll(self.vk_session, self.group_id)
        self.vk = self.vk_session.get_api()

        self.chats = self.get_all_chats()

    def listen(self):
        """
            Function of listen events
        """

        club = f'club{self.group_id}'
        chat = None

        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat \
                    and club in event.message.text:

                chat_id = event.chat_id
                user_id = event.message.from_id
                text = event.message.text

                if chat is None:
                    chat = Chat(self.vk, chat_id)
                else:
                    if not chat.id == chat_id:
                        chat = Chat(self.vk, chat_id)

                user = chat.get_info_user(user_id)
                clean_text = text[text.find(']') + 2: len(text)]

                if '!ban' in clean_text:
                    if user.is_admin:
                        banned_user_id = self.__get_clean_id(clean_text)
                        chat.get_info_user(banned_user_id).ban_user()
                    else:
                        user.send_message_to_user(
                            'У вас недостаточно прав для данной команды!')
                elif '!hackerrank_help' in clean_text:
                    chat.hackerrank_help()
                elif '!hackerrank' in clean_text:
                    lang = clean_text[len('!hackerrank') + 1: len(clean_text)]
                    chat.hackerrank(lang)
                elif '!help' == clean_text:
                    chat.help_user()
                elif '!help_admin' == clean_text:
                    if user.is_admin:
                        chat.help_admin()
                    else:
                        user.send_message_to_user(
                            'У вас недостаточно прав для данной команды!')
                elif '!nemezida' == clean_text:
                    chat.nemezida()
                elif '!warns' == clean_text:
                    user.get_count_warns()
                elif '!warn' in clean_text:
                    if user.is_admin:
                        warn_user_id = self.__get_clean_id(clean_text)
                        warn_user = chat.get_info_user(warn_user_id)
                        chat.warn_user(warn_user)
                    else:
                        user.send_message_to_user(
                            'У вас недостаточно прав для данной команды!')
                elif '!meetup' in clean_text:
                    # TODO: Check len of string for catch a exception
                    content = re.findall('".+?"', clean_text)
                    name = content[0][1:len(content[0]) - 1]
                    ref = content[1][1:len(content[1]) - 1]
                    chat.notice_meetup(name, ref)
                elif '!unwarn' in clean_text:
                    if user.is_admin:
                        unwarn_user_id = self.__get_clean_id(clean_text)
                        unwarn_user = chat.get_info_user(unwarn_user_id)
                        chat.unwarn_user(unwarn_user)
                    else:
                        user.send_message_to_user(
                            'У вас недостаточно прав для данной команды!')
                else:
                    chat.unknown_command()

    def notice_all(self, name, ref):
        for chat in self.chats:
            _chat = Chat(self.vk, chat)
            _chat.notice_meetup(name, ref)

    def get_all_chats(self):
        chats = []
        response = self.vk.messages.getConversations()
        for chat in response['items']:
            if chat['conversation']['peer']['type'] == 'chat':
                chats.append(chat['conversation']['peer']['local_id'])
        return chats

    def __get_clean_id(self, user_id):
        clean_id = user_id[user_id.find('id') + 2: user_id.find('|')]

        if not clean_id.isdigit():
            raise 'InvalidAgruments'
            return None
        else:
            return clean_id
