from django.contrib import admin
from .models import Role, RequestHelp, RequestSupport, Person, VK, Telegram, Subject

# Register your models here.

admin.site.register(Role)
admin.site.register(RequestHelp)
admin.site.register(RequestSupport)
#admin.site.register(RequestRating)
admin.site.register(Person)
admin.site.register(VK)
admin.site.register(Telegram)
admin.site.register(Subject)