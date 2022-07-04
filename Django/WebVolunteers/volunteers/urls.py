from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views


urlpatterns = [
    path('close_request_help/<int:request_number>/', views.closeRequestHelp, name='closeRequestHelp'),
    path('detail_request_help/<int:request_number>/', views.detailRequestHelp, name='detailRequestHelp'),
    path('request_help/', views.requestHelp, name='requestHelp'),
    path('open_request_help/', views.openRequestHelp, name='openRequestHelp'),
    path('closed_request_help/', views.closedRequestHelp, name='closedRequestHelp'),
    path('accept_request_help/<int:request_number>/', views.acceptRequestHelp, name='acceptRequestHelp'),
    path('cancel_request_help/<int:request_number>/', views.cancelRequestHelp, name='cancelRequestHelp'),
    path('my_request_help/', views.myRequestHelp, name='myRequestHelp'),
    path('login/', views.login, name="login"),
    path('api/v1/request_help.json', views.RequestHelpAPIv1View.as_view(), name='request_help_apiv1'),
    path('api/v1/persons.json', views.PersonAPIv1View.as_view()),
    path('oauth/', include('social_django.urls', namespace='social')),  # <--
    path('', views.index, name='index')
]