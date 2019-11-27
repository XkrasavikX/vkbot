from time import sleep
import os
from time import sleep
import sys
from vk_api.longpoll import VkLongPoll, VkEventType

from func import *

# Colors
r, g, b = '\033[31m', '\033[32m', '\033[34m'

try:
    with open("configs.json", "r") as f:
        configs = json.load(f)
        token = configs["token"]
        group_id = configs["group_id"]

except:
    print(r + "[-] Не удалось открыть файл с token и id group!")
    raise
    exit()

try:
    vk_session = vk_api.VkApi(token=token)
    longpoll = VkLongPoll(vk_session)
    session_api = vk_session.get_api()

except:
    print(r + "[-] Не удалось авторизироваться! Проверьте токен и id сообщества!")
    raise
    exit()

answer = {"го": "ГО"}

clear = lambda: os.system('cls' if os.name == 'nt' else 'clear')

time = lambda: datetime.datetime.today().strftime("[%H:%M:%S]")


def console(module=''):
    return b + 'vk/dev/' + module + '$> '


def conversations():
    conversation = session_api.messages.getConversations(filter="all", offset=0)
    print("Общее число сообщений:", conversation["count"])
    for chats in conversation["items"]:
        print("id" + str(chats["conversation"]["peer"]["id"]) + " " + chats["last_message"]["text"])


def answering_machine():
    while True:
        try:
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    msg = event.text.lower()
                    if not event.from_me:
                        print(g + time() + '[i] Новое сообщение от пользователя @id' + str(
                            event.peer_id) + ' Текст сообщения:' + msg)
                        try:
                            session_api.messages.send(peer_id=event.peer_id,
                                                      random_id=random.randint(1, 922337203685477580),
                                                      message=answer[msg] if msg in answer else 'Ты кто?')
                        except:
                            raise

        except:
            print(r + time() + "Потеря соединение! проверьте интернет-соединение!")
            sleep(300)
            continue
            raise


def choose(num):
    clear()
    if num == '0':
        exit()
    elif num == '1':
        always_online()
    elif num == '2':
        conversations()
    elif num == '3':
        answering_machine()
    elif num == '4':
        note(text=input(console('note')), title=input(console('note')))
    elif num == '5':
        print(g + time() + "[i]Starting mailing")
        mailing(message=input(console('malling')))
        print(g + time() + "[i]Finish mailing")
clear()
print(g + "\nLoading..")
for i in range(10):
    sys.stdout.write('*')
    sys.stdout.flush()
    sleep(.3)
    sys.stdout.write('\n')
clear
while True:
    print(b + '   __      ___  __       _                _              _      \n'
              '   \ \    / / |/ /      | |              | |            | |     \n'
              '    \ \  / /|   /     __| | _____   __   | |_ ___   ___ | |___  \n'
              '     \ \/ / |  <     / _` |/ _ \ \ / /   | __/ _ \ / _ \| / __| \n'
              '      \  /  | . \   | (_| |  __/\ V /    | || (_) | (_) | \__ \\\n'
              '       \/   |_|\_\   \__,_|\___| \_/      \__\___/ \___/|_|___/ ', g, '\n',
          '———————————————————————————————————————————————————————————————\n'
          '1 — Вечный онлайн\n'
          '2 — Диалоги \n'
          '3 — Автоответчик\n'
          '4 — Создание заметки (Group tool)\n'
          '5 — Рассылка (Group tool)\n'
          '0 — exit')
    choose(input(console()))
