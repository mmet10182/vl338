#from django.contrib.auth import views as auth_views, logout
from django.contrib.auth.views import LogoutView
from django.conf.urls import url
from django.contrib.auth import logout
from django.urls import path, include
from . import views


urlpatterns = [
    path('vl_user_add/<int:user_id>', views.vlUserAdd, name='vlUserAdd'),
    path('vl_user_manage/<int:user_id>', views.vlUserManage, name='vlUserDetail'),
    path('vl_subjects/', views.vlSubjects, name='vlSubjects'),
    path('vl_users/', views.vlUsers, name='vlUsers'),
    path('vl_admin/', views.vlAdmin, name='vlAdmin'),
    path('close_request_help/<int:request_number>/', views.closeRequestHelp, name='closeRequestHelp'),
    path('detail_request_help/<int:request_number>/', views.detailRequestHelp, name='detailRequestHelp'),
    path('request_help/', views.requestHelp, name='requestHelp'),
    path('open_request_help/', views.openRequestHelp, name='openRequestHelp'),
    path('process_request_help/', views.processRequestHelp, name='processRequestHelp'),
    path('closed_request_help/', views.closedRequestHelp, name='closedRequestHelp'),
    path('accept_request_help/<int:request_number>/', views.acceptRequestHelp, name='acceptRequestHelp'),
    path('cancel_request_help/<int:request_number>/', views.cancelRequestHelp, name='cancelRequestHelp'),
    path('my_request_help/', views.myRequestHelp, name='myRequestHelp'),
    path('login/', views.login, name="login"),
    path('api/v1/request_help.json', views.RequestHelpAPIv1View.as_view(), name='request_help_apiv1'),
    path('api/v1/persons.json', views.PersonAPIv1View.as_view()),
    path('api/v1/subjects.json', views.SubjectAPIv1View.as_view()),
    path('oauth/', include('social_django.urls', namespace='social')),  # <--
    url(r'^logout$', LogoutView.as_view(),  name='logout'),
    #path('logout/', logout, {'next_page': '/'}, name='logout'),
    #path('logout/',LogoutView.as_view(), name='logout'),
    path('', views.index, name='index')
]