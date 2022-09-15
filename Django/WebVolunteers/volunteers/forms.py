from django import forms
from .models import Subject, Person
from django.forms import TextInput


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ('subject_name',)


# class PersonForm(forms.ModelForm):
#     class Meta:
#         model = Person
#         fields = ('last_name','first_name', 'patronymic', 'classroom', 'phone_number',)
#
#         widgets = {
#             'last_name': TextInput(attrs={
#                 'class': 'form-control',
#                  'value': #TODO how to pass value from db
#             }),
#         }