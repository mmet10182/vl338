import re

from django.http import HttpResponse

from .volunteersLIB import VolunteersPerson


class UserRoles:
    def __init__(self, get_responce):
        self.get_responce = get_responce

    def __call__(self, request):
        if request.method == 'GET':

            user_id = request.user.id
            if re.search('id[0-9]+', request.user.username):
                user_id = request.user.username[2:]

            person = VolunteersPerson(user_id)
            # context = {
            #     'reqs': RequestHelp.objects.all() if request.user.is_authenticated else []
            # }
            # TODO
            context = {
                'user_id': person.get_id(),
                'roles': person.get_roles(),
            }
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!', request)
            print(context)
        #return self.get_responce(request)
        return HttpResponse(context)
