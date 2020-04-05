import vk_bot

token = 'your_token'
group_id = 'your_group_id'


if __name__ == "__main__":
    bot = vk_bot.VKBot(token, group_id)
    while True:
        try:
            bot.listen()
        except Exception as err:
            print(f'Error: {err}\n Restarting bot...')
