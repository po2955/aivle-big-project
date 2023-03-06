from django.contrib import admin
from .models import AI_Model, Alarm, Accident
# Register your models here.
# ID admin PW admin
admin.site.register(AI_Model)
admin.site.register(Alarm)
admin.site.register(Accident)
