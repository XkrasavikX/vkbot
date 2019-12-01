from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import vk_api, datetime, random, json

token = ''
group_id = ''

vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
followers = session_api.messages.getConversations()

time = lambda: datetime.datetime.today().strftime("[%H:%M:%S]")


# функция для отправки сообщения
def send_message(peer_id, message=None, attachment=None, keyboard=None):
    session_api.messages.send(
        peer_id=peer_id,
        random_id=random.randint(1, 922337203685477580),
        message=message)


# функция которая возвращяет id людей которые писали
def get_dialogs():
    followers = session_api.messages.getConversations()
    for i in range(followers['count']):
        print(str(followers['items'][i]['conversation']['peer']['id']))


# Вечный онлайн
def always_online():
    while True:
        try:
            time.sleep(300)
            session_api.account.setOnline()
        except:
            continue
            raise

        # функция для создания заметки


def note(title, text):
    session_api.notes.add(title=title, text=text)


# функция для рассылки
def mailing(message='Тестовая рассылка'):
    fail = 0
    followers = session_api.messages.getConversations()
    for i in range(followers['count']):
        try:
            send_message(peer_id=followers['items'][i]['conversation']['peer']['id'], message=message)
        except:
            fail += 1
            continue
            raise
    print("count of Fail mailings:", fail)
