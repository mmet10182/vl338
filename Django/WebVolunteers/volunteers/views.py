from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import RequestHelp, Person, VK, Telegram, Role, Subject
from .serializers import PersonSerializer, RequestHelpSerializer, SubjectSerializer
from .volunteersLIB import VolunteersRequest, gen_request_number, roleVolunteer, VolunteersDetailHelp, GENERAL_URL, \
    VolunteersPerson, ratingValue
import re
from django.conf import settings
from .forms import SubjectForm


# Create your views here.


class PersonAPIv1View(generics.ListAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


# class RequestHelpAPIv1View(generics.ListAPIView):
#    queryset = RequestHelp.objects.all()
#    serializer_class = RequestHelpSerializer


class RequestHelpAPIv1View(APIView):
    def get(self, request):
        req_help = RequestHelp.objects.all()
        serializer = RequestHelpSerializer(req_help, many=True)
        return Response({'posts': serializer.data})

    def post(self, request):
        # The request comes from the client as a QueryDict, convert it into a standard dictionary
        from_client = dict(request.data.lists())
        # Dictionary values are represented as a list, resave the value as a string
        for k, v in from_client.items():
            from_client.update({k: v[0]})

        volutr_req = VolunteersRequest(from_client=from_client)

        if volutr_req.check_from_msg() is False:
            return HttpResponse('This field is required or the sender is not supported')

        if volutr_req.check_user_id() is False:
            return HttpResponse('user_id is required')

        if volutr_req.detect_user_db() is False and volutr_req.from_msg == 'VK':
            print('Create user VK')
            # Save user VK
            vk = VK(user_id=volutr_req.user_id, first_name=volutr_req.first_name, last_name=volutr_req.last_name)
            vk.save()
            # Save Person
            person = Person(first_name=volutr_req.first_name, last_name=volutr_req.last_name,
                            phone_number=volutr_req.phone_number, vk=vk)
            person.save()
            # Save Role
            role = Role(learner=True, person=person)
            role.save()

        elif volutr_req.detect_user_db() is not False and volutr_req.from_msg == 'VK':
            person = Person.objects.get(vk__user_id=volutr_req.user_id)

        # TODO the block not completed
        if volutr_req.detect_user_db() is False and volutr_req.from_msg == 'Telegram':
            print('Create user Telegram')
            telegram = Telegram(user_id=volutr_req.user_id, first_name=volutr_req.first_name,
                                last_name=volutr_req.last_name, username=volutr_req.telegram_username)
            telegram.save()

        # Create a new QueryDict object because in the request.data from the client comes without field needed
        # request_number. request.date - the QueryDict object is not a mutable object
        reques_number = gen_request_number()
        detail_request_link = str(GENERAL_URL+'detail_request_help/'+reques_number)
        from_client.update({'request_number': reques_number,
                            'creator': person.id,
                            'detail_request_link': detail_request_link})
        query_dict = QueryDict('', mutable=True)
        query_dict.update(from_client)
        serializer = RequestHelpSerializer(data=query_dict)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(from_client)


class SubjectAPIv1View(APIView):

    def get(self, request):
        subject = Subject.objects.all()
        serializer = SubjectSerializer(subject, many=True)
        return Response({'posts': serializer.data})



@login_required
def index(request):
    if request.method == 'GET':
        request_open = len(RequestHelp.objects.filter(status='Open'))
        request_closed = len(RequestHelp.objects.filter(status='Closed'))
        request_process = len(RequestHelp.objects.filter(status='InProcess'))
        context = {
            'request_open': request_open,
            'request_closed': request_closed,
            'request_process': request_process}
        return render(request, 'base.html', context)


def login(request):
    context = {'api_id': settings.SOCIAL_AUTH_VK_OAUTH2_KEY}
    return render(request, 'login.html', context=context)


@login_required
def requestHelp(request):
    if request.method == 'GET':

        user_id = request.user.id
        if re.search('id[0-9]+', request.user.username):
            user_id = request.user.username[2:]

        context = {}
        try:
            role = Role.objects.get(person__vk__user_id=user_id)
            context = {
                'access_admin': True if role.admin else False,
                'access_volunteer': True if role.volunteer else False,
                'access_learner': True if role.learner else False,
            }
            if role.admin is False and role.volunteer is False and role.learner is False:
                context.update({'access': False})
        except Role.DoesNotExist:
            context.update({'access': False})

        return render(request, 'request_help.html', context)


@login_required
def openRequestHelp(request):
    if request.method == 'GET':

        user_id = request.user.id
        if re.search('id[0-9]+', request.user.username):
            user_id = request.user.username[2:]

        role = Role.objects.get(person__vk__user_id=user_id)

        context = {
            'access_admin': True if role.admin else False,
            'access_volunteer': True if role.volunteer else False,
            'access_learner': True if role.learner else False,
            'reqs': RequestHelp.objects.filter(status='Open') if request.user.is_authenticated else [],
        }

        return render(request, 'open_request_help.html', context)


@login_required
def processRequestHelp(request):
    if request.method == 'GET':

        user_id = request.user.id
        if re.search('id[0-9]+', request.user.username):
            user_id = request.user.username[2:]

        role = Role.objects.get(person__vk__user_id=user_id)

        context = {
            'access_admin': True if role.admin else False,
            'access_volunteer': True if role.volunteer else False,
            'access_learner': True if role.learner else False,
            'reqs': RequestHelp.objects.filter(status='InProcess') if request.user.is_authenticated else [],
        }

        return render(request, 'process_request_help.html', context)


@login_required
def closedRequestHelp(request):
    if request.method == 'GET':
        user_id = request.user.id
        if re.search('id[0-9]+', request.user.username):
            user_id = request.user.username[2:]

        role = Role.objects.get(person__vk__user_id=user_id)
        context = {
            'access_admin': True if role.admin else False,
            'access_volunteer': True if role.volunteer else False,
            'access_learner': True if role.learner else False,
            'reqs': RequestHelp.objects.filter(status='Closed') if request.user.is_authenticated else [],
            #'rating_val': ratingValue(),
        }
        #print(context['rating_val'])
        return render(request, 'closed_request_help.html', context)


@login_required
def closeRequestHelp(request, request_number=0):
    if request.method == 'GET':
        request_help = RequestHelp.objects.get(request_number=request_number)
        request_help.status = 'Closed'
        request_help.rating = request.GET['rating']
        request_help.save()
        current_page = request.META.get('HTTP_REFERER')
        return HttpResponseRedirect(current_page)


@login_required
def acceptRequestHelp(request, request_number=0):
    if request.method == 'GET':
        # user_id - will be the id of the system through which the user logged in (vk or telegram)
        user_id = request.user.id
        if re.search('id[0-9]+', request.user.username):
            user_id = request.user.username[2:]

        person = Person.objects.get(vk__user_id=user_id)
        # person_id - internal id assigned by the database
        person_id = person.id

        request_help = RequestHelp.objects.get(request_number=request_number)
        # Only members of the volunteer or admin role can accept request_help
        permission = False
        role = Role.objects.get(person=person_id)
        if role.admin or role.volunteer:
            permission = True
        else:
            return render(request, 'accept_request_help.html', context={'permission': permission})
        # The creator of the request_help cannot accept the request_help that himself created
        # creator_id - id assigned by the database, not VK or Telegram
        creator_id = request_help.creator.id
        myself = False
        if person_id == creator_id:
            myself = True
            return render(request, 'accept_request_help.html', context = {'myself': myself})

        request_help.owner = person
        request_help.status = 'InProcess'
        request_help.save()
        request_help = RequestHelp.objects.get(request_number=request_number)
        context = {
            'user_id': user_id,
            'person_id': person_id,
            'request_number': request_number,
            'owner': request_help.owner.first_name,
            'myself': myself,
            'permission': permission,
        }

        return render(request, 'accept_request_help.html', context)


@login_required
def cancelRequestHelp(request, request_number=0):
    if request.method == 'GET':

        user_id = request.user.id
        if re.search('id[0-9]+', request.user.username):
            user_id = request.user.username[2:]

        # person = Person.objects.get(vk__user_id=user_id)
        # person_id = person.id
        request_help = RequestHelp.objects.get(request_number=request_number)
        request_help.owner = None
        request_help.status = 'Open'
        request_help.save()
        request_help = RequestHelp.objects.get(request_number=request_number)
        context = {
            'request_number': request_number,
            'status': request_help.status,
        }

        return render(request, 'cancel_request_help.html', context)


@login_required
def myRequestHelp(request):
    if request.method == 'GET':

        user_id = request.user.id
        if re.search('id[0-9]+', request.user.username):
            user_id = request.user.username[2:]

        request_help_owner = RequestHelp.objects.filter(owner__vk__user_id=user_id)
        request_help_creator = RequestHelp.objects.filter(creator__vk__user_id=user_id)
        role = Role.objects.get(person__vk__user_id=user_id)

        context = {
            'access_admin': True if role.admin else False,
            'access_volunteer': True if role.volunteer else False,
            'access_learner': True if role.learner else False,
            'owner_items': request_help_owner,
            'creator_items': request_help_creator
        }
        return render(request, 'my_request_help.html', context)


@login_required
def detailRequestHelp(request, request_number=0):
    if request.method == 'GET':

        user_id = request.user.id
        if re.search('id[0-9]+', request.user.username):
            user_id = request.user.username[2:]

        person_id = Person.objects.get(vk__user_id=user_id)
        person_id = person_id.id

        try:
            query_request_help = RequestHelp.objects.get(request_number=request_number)
        except RequestHelp.DoesNotExist:
            query_request_help = None

        details = VolunteersDetailHelp(query_request_help)
        # Request_help creator can view detailed information
        permission = False
        if person_id == details.owner_id or person_id == details.creator_id:
            permission = True
        print(permission)
        context = {
            'request_number': details.request_number,
            'Subject': details.subject,
            'Theme': details.theme,
            'creator_first_name': details.creator_first_name,
            'creator_last_name': details.creator_last_name,
            'creator_vk_id': details.creator_vk_id,
            'creator_telegram_id': details.creator_telegram_id,
            'owner': details.owner,
            'owner_first_name': details.owner_first_name,
            'owner_last_name': details.owner_last_name,
            'owner_vk_id': details.owner_vk_id,
            'owner_telegram_id': details.owner_telegram_id,
            'status': details.status,
            'creation_time': details.creation_time,
            'creation_date': details.creation_date,
            'permission': permission,
        }
        return render(request, 'detail_request_help.html', {'details': context})


@login_required
def vlAdmin(request):
    return render(request, 'vl_admin.html', {'admin': 'Manage the site'})


@login_required
def vlSubjects(request):
    err = ''
    subj_form = SubjectForm(request.POST)

    if request.method == 'POST':
        if subj_form.is_valid():
            print('Form is valid')
            subj_form.save()
        return redirect('vlSubjects')

    subjs = Subject.objects.all()
    context = {'subj_form': subj_form,
               'subjs': subjs,
               'err': err}

    return render(request, 'vl_subjects.html', context=context)


@login_required
def vlUsers(request):
    persons = Person.objects.all()
    list_persons = []
    for person in persons:
        roles = Role.objects.get(person=person)
        #TODO
        print('{} {}'.format(person.last_name, roles))
        for i in roles:
            print(i)
        person = {'first_name': person.first_name,
                  'last_name': person.last_name,
                  'vkid': person.vk.user_id,
                  'id': person.id,
                  'roles': roles}
        list_persons.append(person)
    context = {'persons': list_persons}
    return render(request, 'vl_users.html', context=context)