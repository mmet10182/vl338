import re
from .volunteersLIB import VolunteersPerson


def get_user_roles(request):
    if request.method == 'GET':
        user_id = request.user.id
        if re.search('id[0-9]+', request.user.username):
            user_id = request.user.username[2:]

        person = VolunteersPerson(user_id)

        context = {
            'user_id': person.get_id(),
            'roles': person.get_roles(),
        }
        return context


def get_user_name(request):
    if request.method == 'GET':
        context = {
            'VK_first_name': request.user.first_name,
            'VK_last_name': request.user.last_name
        }
        return context