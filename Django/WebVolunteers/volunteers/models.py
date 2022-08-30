from django.db import models
import uuid


# Create your models here.
class Role(models.Model):
    admin = models.BooleanField(default=False)
    learner = models.BooleanField(default=False)
    volunteer = models.BooleanField(default=False)
    person = models.ForeignKey('Person', on_delete=models.SET_NULL, null=True, help_text='Role person')

    def __str__(self):
        return '{} {}'.format(self.person.first_name, self.person.last_name)


class Person(models.Model):
    first_name = models.CharField(max_length=20, blank=True, null=True, help_text="Enter first name")
    last_name = models.CharField(max_length=20, blank=True, null=True, help_text="Enter last name")
    patronymic = models.CharField(max_length=20, blank=True, null=True, help_text="Enter patronymic name")
    classroom = models.CharField(max_length=3, blank=True, null=True, help_text="Enter classroom name")
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="telegram name")
    vk = models.OneToOneField('VK', on_delete=models.CASCADE, blank=True, null=True, related_name='Person_VK')
    telegram = models.OneToOneField('Telegram', on_delete=models.CASCADE, blank=True, null=True, related_name='Person_Telegram')

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)


class RequestHelp(models.Model):
    creator = models.ForeignKey(Person, null=True, on_delete=models.CASCADE, related_name='help_creator')
    subject = models.CharField(max_length=20, null=False, help_text="Subject")
    theme = models.CharField(max_length=200, null=False, help_text="Theme")
    status = models.CharField(max_length=20, null=False, default='Open', help_text="Status")
    owner = models.ForeignKey(Person, blank=True, null=True, on_delete=models.CASCADE, related_name='help_owner')
    request_number = models.CharField(max_length=20, null=False, help_text="request_number")
    creation_time = models.TimeField(auto_now=True, help_text='creation_time')
    creation_date = models.DateField(auto_now=True, help_text='creation_date')
    rating = models.CharField(max_length=20, null=True, help_text='rating')

    def __str__(self):
        return self.request_number


class RequestSupport(models.Model):
    creator = models.ForeignKey(Person, null=True, on_delete=models.CASCADE, related_name='request_creator')
    message = models.CharField(max_length=20, null=False, help_text="Message")
    status = models.CharField(max_length=20, null=False, help_text="Status")
    owner = models.ForeignKey(Person, null=True, on_delete=models.CASCADE, related_name='request_owner')


# class RequestRating(models.Model):
#     request_help = models.ForeignKey(RequestHelp, default=None, on_delete=models.CASCADE, related_name='request_number_help')
#     creator = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='rating_creator')
#     rating = models.CharField(max_length=20, null=False, help_text="Rating")
#     owner = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='rating_owner')


class VK(models.Model):
    user_id = models.CharField(max_length=20, blank=True, null=True, help_text="vk id")
    first_name = models.CharField(max_length=20, blank=True, null=True, help_text="Enter first name")
    last_name = models.CharField(max_length=20, blank=True, null=True, help_text="Enter last name")


class Telegram(models.Model):
    user_id = models.CharField(max_length=20, blank=True, null=True, help_text="telegram id")
    username = models.CharField(max_length=20, blank=True, null=True, help_text="telegram name")
    first_name = models.CharField(max_length=20, blank=True, null=True, help_text="Enter first name")
    last_name = models.CharField(max_length=20, blank=True, null=True, help_text="Enter last name")


class Subject(models.Model):
    subject_name = models.CharField(max_length=20,unique=True)