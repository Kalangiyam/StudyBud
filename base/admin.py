from django.contrib import admin
from .models import Room,Topic,Message,User

admin.site.site_header = 'Studybud Administration'
# Register your models here.
admin.site.register(User)
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)