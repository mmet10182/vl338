from rest_framework import serializers
from .models import Person, RequestHelp, Subject


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'


class RequestHelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestHelp
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'