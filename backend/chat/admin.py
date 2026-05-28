from django.contrib import admin
from .models import Message, UserStatus

admin.site.register(Message)
admin.site.register(UserStatus)