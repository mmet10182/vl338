from .models import VK, Telegram
from random import randint
from .models import RequestHelp, Person, Role
import re
from decouple import config

FROM_MSG = config('FROM_MSG', cast=lambda v: [s.strip() for s in v.split(',')])
GENERAL_URL = config('GENERAL_URL')


class VolunteersRequest:
    def __init__(self, from_client):
        self.uid = None
        self.first_name = None
        self.last_name = None
        self.patronymic = None
        self.classroom = None
        self.user_id = None
        self.telegram_username = None
        self.phone_number = None
        self.from_msg = None
        self.from_client = from_client

    def check_first_name(self):
        try:
            if self.from_client['first_name']:
                self.first_name = self.from_client['first_name']
                return self.first_name
        except KeyError:
            return False

    def check_last_name(self):
        try:
            if self.from_client['last_name']:
                self.last_name = self.from_client['last_name']
                return self.last_name
        except KeyError:
            return False

    def check_from_msg(self):
        try:
            if self.from_client['from_msg'] in FROM_MSG:
                self.from_msg = self.from_client['from_msg']
                return self.from_msg
            else:
                return False
        except KeyError:
            return False

    def check_user_id(self):
        try:
            if self.from_client['user_id']:
                self.user_id = self.from_client['user_id']
                return self.user_id
        except KeyError:
            return False

    def detect_user_db(self):
        if self.from_msg == 'VK':
            user_id = VK.objects.filter(user_id=self.user_id)
            if user_id.exists():
                return user_id
            else:
                self.first_name = self.from_client['first_name']
                self.last_name = self.from_client['last_name']
                return False
        # TODO The block not tested
        if self.from_msg == 'Telegram':
            user_id = Telegram.objects.filter(user_id=self.user_id)
            if user_id.exists():
                return user_id
            else:
                self.first_name = self.from_client['first_name']
                self.last_name = self.from_client['last_name']
        return False


class VolunteersRequestHelp(VolunteersRequest):
    def __init__(self):
        super().__init__()
        self.creator = None
        self.subject = None
        self.theme = None
        self.status = None
        self.owner = None
        self.request_number = None


class VolunteersRequestSupport(VolunteersRequest):
    pass


class VolunteersRequestRating(VolunteersRequest):
    pass


def gen_request_number():
    return str(randint(10000, 999999))


class VolunteersDetailHelp:
    def __init__(self, query_request_help):
        self.request_number = None
        self.subject = None
        self.theme = None
        self.creator_first_name = None
        self.creator_last_name = None
        self.creator_vk_id = None
        self.creator_telegram_id = None
        self.owner = None
        self.owner_first_name = None
        self.owner_last_name = None
        self.owner_vk_id = None
        self.owner_telegram_id = None
        self.status = None
        self.creation_time = None
        self.creation_date = None
        self.query_request_help = query_request_help
        self.__check_Field()

    def __check_Field(self):
        if self.query_request_help is None:
            return False

        try:
            self.request_number = self.query_request_help.request_number
        except AttributeError:
            self.request_number = None

        try:
            self.subject = self.query_request_help.subject
        except AttributeError:
            self.subject = None

        try:
            self.theme = self.query_request_help.theme
        except AttributeError:
            self.theme = None

        try:
            self.creator_first_name = self.query_request_help.creator.first_name
        except AttributeError:
            self.creator_first_name = None

        try:
            self.creator_last_name = self.query_request_help.creator.last_name
        except AttributeError:
            self.creator_last_name = None

        try:
            self.creator_vk_id = self.query_request_help.creator.vk.user_id
        except AttributeError:
            self.creator_vk_id = None

        try:
            self.creator_telegram_id = self.query_request_help.creator.telegram.user_id
        except AttributeError:
            self.creator_telegram_id = None

        try:
            self.owner = self.query_request_help.owner
        except AttributeError:
            self.owner = None

        try:
            self.owner_first_name = self.query_request_help.owner.first_name
        except AttributeError:
            self.owner_first_name = None

        try:
            self.owner_last_name = self.query_request_help.owner.last_name
        except AttributeError:
            self.owner_last_name = None

        try:
            self.owner_vk_id = self.query_request_help.owner.vk.user_id
        except AttributeError:
            self.owner_vk_id = None

        try:
            self.owner_telegram_id = self.query_request_help.owner.telegram.user_id
        except AttributeError:
            self.owner_telegram_id = None

        try:
            self.status = self.query_request_help.status
        except AttributeError:
            self.status = None

        try:
            self.creation_time = self.query_request_help.creation_time
        except AttributeError:
            self.creation_time = None

        try:
            self.creation_date = self.query_request_help.creation_date
        except AttributeError:
            self.creation_date = None


class VolunteersPerson:
    def __init__(self, user_id):
        self.user_id = user_id

    def get_roles(self):

        user_id = self.get_id()
        roles = []

        if self.user_id:
            try:
                query_roles = Role.objects.get(person__id=user_id)
            except Role.DoesNotExist:
                return False

            if query_roles.admin:
                roles.append('Admin')
            if query_roles.learner:
                roles.append('Learner')
            if query_roles.volunteer:
                roles.append('Volunteer')
        else: return False
        return roles

    def get_id(self):
        """
        The method return person ID from database
        """
        vk_id = None
        telegram_id = None
        if self.user_id is not None:
            try:
                person = Person.objects.get(vk__user_id=self.user_id)
                return person.id
            except Person.DoesNotExist:
                vk_id = False

            try:
                print(self.user_id)
                person = Person.objects.get(telegram__user_id=self.user_id)
                return person.id
            except Person.DoesNotExist:
                telegram_id = False

        if vk_id is False and telegram_id is False:
            return False


def roleVolunteer(func):
    def wrapper(*args, **kwargs):
        print('1: ', args)
        print('2: ', kwargs)
        context = func(*args, **kwargs)
        print(context)
        return context

    return wrapper


def ratingValue(value):
    rating = {'1': 'Остались вопросы',
              '2': 'Хорошо',
              '3': 'Отлично',
              }
    return rating[value]