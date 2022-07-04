import json
import requests
from config import WEB_API_BACKEND
import re

class Dialog:
    def __init__(self, user_id=None, peer_id=None, event_id=None, subject=None, theme=None, answer=None, rating=0,
                 type_dialog=None, msg_from_user=None, dialog=None, vk=None, random_id=None, keyboard=None,
                 message=None, subjects=None, from_id=None, send_notify=None, dialog_del=None, first_name=None,
                 last_name=None, telegram=None, telegram_chat_id=None, question_count=0, rating_count=0,
                 volunteer_name=None, keyboard_rating=None):
        self.subject_count = 0
        self.user_id = user_id
        self.peer_id = peer_id
        self.event_id = event_id
        self.subject = subject
        self.theme = theme
        self.answer = answer
        self.rating = rating
        self.type_dialog = type_dialog
        self.msg_from_user = msg_from_user
        self.dialog = dialog
        self.vk = vk
        self.random_id = random_id
        self.keyboard = keyboard
        self.keyboard_rating = keyboard_rating
        self.message = message
        self.subjects = subjects
        self.from_id = from_id
        self.send_notify = send_notify
        self.dialog_del = dialog_del
        self.first_name = first_name
        self.last_name = last_name
        self.telegram = telegram
        self.telegram_chat_id = telegram_chat_id
        self.question_count = question_count
        self.rating_count = rating_count
        self.volunteer_name = volunteer_name

    def send_msg(self, vk=None, random_id=None, keyboard=None, message=None, admin_user_id=None):
        if vk is None or random_id is None or message is None:
            return 'Missing parameters'
        if keyboard:
            vk.messages.send(
                from_id=self.from_id,
                random_id=random_id,
                peer_id=self.peer_id,
                keyboard=keyboard.get_keyboard(),
                message=message)
        elif admin_user_id:
            vk.messages.send(
                user_id=admin_user_id,
                from_id=self.from_id,
                random_id=random_id,
                # peer_id=self.peer_id,
                message=message)
        else:
            vk.messages.send(
                from_id=self.from_id,
                random_id=random_id,
                peer_id=self.peer_id,
                message=message)

    def send_msg_telegram(self, message):
        if self.telegram is None and self.telegram_chat_id is None:
            return 'Missing paramets'
        self.telegram.send_message(self.telegram_chat_id, message)

    def send_json_DRF(self):
        url = WEB_API_BACKEND + 'request_help.json'
        data = {
            'from_msg': 'VK',
            'first_name': self.first_name,
            'last_name': self.last_name,
            'subject': self.subject,
            'theme': self.theme,
            'user_id': self.user_id,
        }
        req_drf = requests.post(url, data)
        # FIXME: Необходимо сделать проверку ответа, как минимум поверить request_number
        print('send_json_DRF', req_drf.text)
        return json.loads(req_drf.text)

    def run(self, from_id, random_id):
        self.from_id = from_id

        if self.type_dialog == 'help':
            if self.msg_from_user in self.subjects:
                self.subject = self.msg_from_user
                return self.send_msg(vk=self.vk, random_id=random_id, message='Введи тему')
            if not self.subject:
                if self.subject_count == 0:
                    self.send_msg(vk=self.vk, random_id=random_id, message='Введи предмет')
                else:
                    self.send_msg(vk=self.vk, random_id=random_id,
                                  message='К сожалению такого предмета нет в списке.\n'
                                          'Убедись в том что ты правильнно ввел название предмета.\n'
                                          'Или на пиши в тех. поддержку о проблеме.')
                self.subject_count += 1
                print(self.subject_count)
            if self.subject:
                self.theme = self.msg_from_user
                # Отправляем уведомление
                print('Send notify')
                # Обозначем что диалог закончен
                self.dialog_del = True
                self.send_notify = True
                # Отправляем json в DRF чать
                # Если все хорошо получим json сохраненной заявки в котором будут номер заявки, статус, ссылка на запрос
                # и еще ряд полей
                answer_DRF = self.send_json_DRF()
                self.request_number = answer_DRF['request_number']
                # Сообщение пользвателю
                print(answer_DRF)
                message = 'Ты ввел\nпредмет:{}\n' \
                          'тема:{}\n' \
                          'Номер твоей заявки:{}\n' \
                          'Управление заявкой: {}\n' \
                          'Жди скоро с тобой свяжутся и помогут.\n' \
                          'Спасибо за обращение.\n' \
                          'Пока.'
                self.send_msg(vk=self.vk, random_id=random_id, message=message.format(self.subject, self.theme,
                            answer_DRF['request_number'], answer_DRF['detail_request_link']))
                # Сообщение админу
                # essage_to_admin = 'Пользователь {} отправил запрос - Предмет: {} Тема: {}'\
                #   .format(self.user_id, self.subject, self.theme)
                message_to_admin = 'Сообщение от VkCahtBot\n' \
                                   'Тип Сообщения: Помощь\n' \
                                   'ID пользовтеля в ВК: {}\n' \
                                   'Пользователь: {} {}\n' \
                                   'Предмет: {}\n' \
                                   'Тема: {}\n' \
                                   'Номер заявки: {}\n' \
                                   'Вязть заявку: {}\n' \
                    .format(self.user_id, self.first_name, self.last_name, self.subject, self.theme,
                            answer_DRF['request_number'], answer_DRF['detail_request_link'])

                self.send_msg_telegram(message_to_admin)
                return self.send_msg(vk=self.vk, random_id=random_id, admin_user_id=2729804,
                                     message=message_to_admin)

        if self.type_dialog == 'question':
            # Счетчик сообщений. Если это 2е сообщение отправляем его админам
            if self.question_count >= 1:
                message_to_user = 'Отлично!\n' \
                                  'Я обязательно передам админам твое сообщение.' \
                                  '\nХорошего дня.' \
                                  '\nСпасибо за обращение.' \
                                  '\nПока.'
                message_to_admin = 'Сообщение от VkCahtBot\n' \
                                   'Тип сообщения: Вопрос.\n' \
                                   'ID пользовтеля в ВК: {}\n' \
                                   'Пользователь: {} {}\n' \
                                   'Пользователь отправил: {}' \
                    .format(self.user_id, self.first_name, self.last_name, self.msg_from_user)
                # Обозначем что диалог закончен
                self.dialog_del = True
                self.send_notify = True
                # Send message to user
                self.send_msg(vk=self.vk, random_id=random_id, message=message_to_user)
                # Send message to admin_group in telegram
                self.send_msg_telegram(message_to_admin)
                # Send message to admin_user in VK
                return self.send_msg(vk=self.vk, random_id=random_id, admin_user_id=2729804, message=message_to_admin)
            else:
                # Send message to user
                message = 'Напиши свое сообщение и я отправлю его админам'
                self.send_msg(vk=self.vk, random_id=random_id, message=message)
            self.question_count = +1

        if self.type_dialog == 'rating':
            # Если это 1е сообщение(в этом типе диалога) отправляем клавиатуру с оценками
            if self.rating_count == 1:
                self.volunteer_name = self.msg_from_user
                print('rating 1 {}'.format(self.rating_count))
                # Send message to user
                message_to_user = 'Оцени оказанную тебе помощь'
                self.send_msg(vk=self.vk, keyboard=self.keyboard_rating, random_id=random_id,
                              message=message_to_user)
            # Счетчик сообщений. Если это 2е сообщение отправляем его админам
            # Сохраняем имя, фамилию волонтера
            elif self.rating_count == 2:
                garde = {'1': 'Отлично',
                         '2': 'Хорошо',
                         '3': 'Ничего не понял'}
                message_to_admin = 'Сообщение от VkCahtBot\n' \
                                   'Тип сообщения: Оценка.\n' \
                                   'ID пользовтеля в ВК: {}\n' \
                                   'Пользователь: {} {}\n' \
                                   'Оценка волонтера: {}. {}' \
                    .format(self.user_id, self.first_name, self.last_name, self.volunteer_name, garde[str(self.rating)])
                message_to_user = 'Рады были помочь.\n' \
                                  'Спасибо.\n' \
                                  'Пока.'
                # Обозначем что диалог закончен
                self.dialog_del = True
                self.send_notify = True
                # Send message to user
                self.send_msg(vk=self.vk, random_id=random_id, message=message_to_user)
                # Send message to admin_group in telegram
                self.send_msg_telegram(message_to_admin)
                # Send message to admin_user in VK
                self.rating_count += 1
                return self.send_msg(vk=self.vk, random_id=random_id, admin_user_id=2729804, message=message_to_admin)
            else:
                # Send message to user
                message = 'Напиши имя и фамилию волонтера оказавшего помощь'
                self.send_msg(vk=self.vk, random_id=random_id, message=message)
            self.rating_count += 1

        # Отправить клавиатуру с кнопками действий
        if self.msg_from_user:
            return self.send_msg(vk=self.vk, random_id=random_id, keyboard=self.keyboard, message=self.message)

    def __str__(self):
        return str(self.user_id)

    def __del__(self):
        if self.vk:
            all_messages = self.vk.messages.getHistory(user_id=self.user_id)
            for i in all_messages['items']:
                if 'keyboard' in i.keys():
                    print('Remove keyboard in chat, message id --- {} \n'.format(i['id']))
                    self.vk.messages.delete(message_ids=str(i['id']), delete_for_all=1)
        print('Dialog object deleted')


def get_dialog(user_id=None, dialogs=None):
    if user_id is None or dialogs is None:
        return 'Set user_id and dialogs'

    for dialog in dialogs:
        if user_id == dialog.user_id:
            return dialog
    return False
