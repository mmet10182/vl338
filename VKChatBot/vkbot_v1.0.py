import json, requests, time
from socket import socket
import urllib3
from vk_api import VkApi
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from VkBotClasses.Dialog import Dialog, get_dialog
import telebot
from config import TELEGRAM_TOKEN, VK_GROUP_TOKEN, VK_API_VERSION, VK_GROUP_ID, TELEGRAM_CHAT_ID, WEB_API_BACKEND
from datetime import datetime
from requests import request

telegramBot = telebot.TeleBot(TELEGRAM_TOKEN)


# Предметы
def get_subjects():
    url = WEB_API_BACKEND + 'subjects.json'
    req = request(method='get', url=url)
    req = json.loads(req.text)
    subjs = []
    for subj in req['posts']:
        subjs.append(str(subj['subject_name']).lower())
    return subjs


# Запускаем бот
vk_session = VkApi(token=VK_GROUP_TOKEN, api_version=VK_API_VERSION)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, group_id=VK_GROUP_ID)

# Клавиатура и настройки для клавиатуры
settings = dict(inline=True)
keyboard = VkKeyboard(**settings)
keyboard.add_callback_button(label='Помощь', color=VkKeyboardColor.PRIMARY,
                             payload={"type": "help", "uid": "123"})
keyboard.add_callback_button(label='Задать вопрос', color=VkKeyboardColor.PRIMARY,
                             payload={"type": "question", "uid": "456"})
keyboard.add_callback_button(label='Оценить', color=VkKeyboardColor.PRIMARY,
                             payload={"type": "rating", "uid": "789"})


def create_keyboard_rating(settings):
    keyboard = VkKeyboard(**settings)
    keyboard.add_callback_button(label='Отлично', color=VkKeyboardColor.PRIMARY,
                                 payload={"type": "1", "uid": "123"})
    keyboard.add_callback_button(label='Хорошо', color=VkKeyboardColor.PRIMARY,
                                 payload={"type": "2", "uid": "456"})
    keyboard.add_callback_button(label='Ничего не понятно', color=VkKeyboardColor.PRIMARY,
                                 payload={"type": "3", "uid": "789"})
    return keyboard


keyboard_rating = create_keyboard_rating(settings)

# сообщения
answer_hello_message = "Привет. Ты готов понять трудную тему? Нужна помощь с домашней работой?\n\n \
                Выбери 'помощь', если да \n \
                Выбери 'задать вопрос', если есть вопросы \n \
                Выбери 'оценить', если волонтеры тебе уже оказали помощь"
# answer_subject_message = 'Введите предмет'
# answer_theme_message = 'Введите тему'
# answer_default_message = 'Я не понимаю, выбери пожалуйста, один из трех вариантов'
# Создаем объект диалога
dialog = Dialog()
dialogs = list()


# Слушаем входящие события от ВК
def run():
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            subjects = get_subjects()
            user_id = event.obj.message['from_id']
            # Получить имя фамилию пользователя(отправителя)
            user_get = vk.users.get(user_ids=(user_id))
            user_get = user_get[0]
            first_name = user_get['first_name']
            last_name = user_get['last_name']
            peer_id = event.obj.message['peer_id']
            msg_from_user = (event.obj.message['text']).lower()
            # Получить диалог с пользователем если есть, если нет вернет False
            dialog = get_dialog(user_id, dialogs)

            print('user_id:{} first_name:{} last_name:{}'.format(user_id, first_name, last_name))

            if dialog:
                dialog.msg_from_user = msg_from_user
                dialog.run(from_id=user_id, random_id=get_random_id())
                # Проверяем можно ли удалять объект.
                if dialog.dialog_del:
                    dialogs.remove(dialog)
                    del dialog
            else:
                dialog_settings = dict(user_id=user_id, peer_id=peer_id, dialog=dialog, vk=vk,
                                       random_id=get_random_id(),
                                       keyboard=keyboard, keyboard_rating=keyboard_rating,
                                       message=answer_hello_message,
                                       msg_from_user=msg_from_user, subjects=subjects, first_name=first_name,
                                       last_name=last_name, telegram=telegramBot, telegram_chat_id=TELEGRAM_CHAT_ID)
                dialog = Dialog(**dialog_settings)
                dialogs.append(dialog)
                dialog = get_dialog(user_id, dialogs)
                dialog.run(from_id=user_id, random_id=get_random_id())
        # События кнопок
        elif event.type == VkBotEventType.MESSAGE_EVENT:
            print('Event buttons', event.object.payload)
            event_id = event.object.event_id
            user_id = event.object.user_id
            peer_id = event.object.peer_id
            dialog = get_dialog(user_id, dialogs)
            dialog.peer_id = peer_id
            dialog.user_id = user_id
            dialog.event_id = event_id
            dialog.vk = vk
            dialog.random_id = get_random_id()

            if event.object.payload.get('type') == 'help':
                user_id = event.object.user_id
                dialog = get_dialog(user_id, dialogs)
                dialog.peer_id = event.object.peer_id
                dialog.user_id = user_id
                dialog.vk = vk
                dialog.random_id = get_random_id()
                dialog.event_id = event.object.event_id
                dialog.type_dialog = 'help'
                dialog.run(from_id=user_id, random_id=get_random_id())
            if event.object.payload.get('type') == 'question':
                print('pressed question')
                user_id = event.object.user_id
                dialog = get_dialog(user_id, dialogs)
                dialog.peer_id = event.object.peer_id
                dialog.user_id = user_id
                dialog.vk = vk
                dialog.random_id = get_random_id()
                dialog.event_id = event.object.event_id
                dialog.type_dialog = 'question'
                dialog.run(from_id=user_id, random_id=get_random_id())
            if event.object.payload.get('type') == 'rating':
                print('pressed rating')
                user_id = event.object.user_id
                dialog = get_dialog(user_id, dialogs)
                print(event.object.peer_id)
                dialog.peer_id = event.object.peer_id
                dialog.user_id = user_id
                dialog.vk = vk
                dialog.random_id = get_random_id()
                dialog.event_id = event.object.event_id
                dialog.type_dialog = 'rating'
                dialog.run(from_id=user_id, random_id=get_random_id())
            if event.object.payload.get('type') == '1':
                print('Pressed grade 1')
                dialog.type_dialog = 'rating'
                dialog.rating = '1'
                vk.messages.sendMessageEventAnswer(event_id=event_id, user_id=user_id, peer_id=peer_id)
                dialog.run(from_id=user_id, random_id=get_random_id())
            if event.object.payload.get('type') == '2':
                print('Pressed grade 2')
                dialog.type_dialog = 'rating'
                dialog.rating = '2'
                vk.messages.sendMessageEventAnswer(event_id=event_id, user_id=user_id, peer_id=peer_id)
                dialog.run(from_id=user_id, random_id=get_random_id())
            if event.object.payload.get('type') == '1':
                print('Pressed grade 3')
                dialog.type_dialog = 'rating'
                dialog.rating = '3'
                vk.messages.sendMessageEventAnswer(event_id=event_id, user_id=user_id, peer_id=peer_id)
                dialog.run(from_id=user_id, random_id=get_random_id())
            if dialog.dialog_del:
                dialogs.remove(dialog)
                del dialog


if __name__ == '__main__':
    now = datetime.now()
    start_time = now.strftime("%H:%M:%S")
    print(start_time)
    try:
        run()
    except requests.exceptions.ReadTimeout:
        now = datetime.now()
        except_time = now.strftime("%H:%M:%S")
        print(except_time)
        time.sleep(3)
        run()
    except AttributeError:
        print('except AttributeError: clicked a button in the chat of a non-existent object ')
        # FIXME
        # This except appears if the user clicked the button before the previous launch of the bot
        # dialog.peer_id = peer_id AttributeError: 'bool' object has no attribute 'peer_id'
        run()
