import vk_api

from vk_api.utils import get_random_id


class User(object):
    def __init__(self, vk, user_id, chat_id, count_warns=0):
        self.vk = vk
        self.chat_id = chat_id
        self.peer_chat_id = chat_id + 2000000000

        self.user_info = self.__get_info_user(user_id)

        self.id = self.user_info['user_id']
        self.first_name = self.user_info['first_name']
        self.last_name = self.user_info['last_name']
        self.is_admin = self.user_info['is_admin']
        self.count_warns = count_warns

    def send_message_to_user(self, message):
        _message = '[id{user_id}|{first_name}], '.format(user_id=self.id,
                                                         first_name=self.first_name) + message
        self.vk.messages.send(chat_id=self.chat_id,
                              message=_message,
                              random_id=get_random_id())

    def send_message(self, message):
        self.vk.messages.send(chat_id=self.chat_id,
                              message=message,
                              random_id=get_random_id())

    def ban_user(self):
        try:
            response = self.vk.messages.removeChatUser(chat_id=self.chat_id,
                                                       user_id=self.id)
        except Exception as ApiError:
            error_msg = ApiError.error['error_msg']
            if error_msg == 'User not found in chat':
                self.send_message_to_user(
                    'пользователя с данным ID нет в беседе!')
            else:
                self.send_message_to_user('некорректный ввод данных!')

    def total_ban_user(self):
        # TODO: Realize this function
        pass

    def get_count_warns(self):
        message = 'у вас {count} из 3 предупреждений!'.format(
            count=self.count_warns)
        self.send_message_to_user(message)

    def warn_user(self):
        self.count_warns += 1

        message = 'вам выдано предупреждение! ({count_warns} из 3)\n'.format(
            count_warns=self.count_warns)

        if self.count_warns == 3:
            message += 'Вы допустили максимальное количество предупреждений!\n'
            self.send_message_to_user(message)
            self.ban_user()
        else:
            message += 'Не нарушайте правила беседы, дабы не быть исключенным из нее!\n'
            self.send_message_to_user(message)

    def unwarn_user(self):
        if self.count_warns == 0:
            self.send_message('У данного пользователя нет предупреждений!')
        else:
            self.count_warns -= 1
            message = ' вам снято предупреждение! (Текущих предупреждений: {count} из 3)'.format(
                count=self.count_warns)
            self.send_message_to_user(message)

    def __get_info_user(self, user_id):
        if type(user_id) != int:
            try:
                user_id = int(user_id)
            except Exception:
                raise ValueError

        response = self.vk.messages.getConversationMembers(
            peer_id=self.peer_chat_id)

        first_data = None
        second_data = None

        for user in response['items']:
            if user['member_id'] == user_id:
                first_data = user
                break

        if first_data is None:
            return None

        for profile in response['profiles']:
            if profile['id'] == user_id:
                second_data = profile
                break

        if second_data is None:
            return None

        return {
            'user_id': user_id,
            'first_name': second_data['first_name'],
            'last_name': second_data['last_name'],
            'is_admin': 'is_admin' in first_data,
        }
