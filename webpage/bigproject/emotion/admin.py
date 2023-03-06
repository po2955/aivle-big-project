from django.contrib import admin

from .models import Emotion
# Register your models here.
class Emotion_Admin(admin.ModelAdmin):
    readonly_fields = ('date',)

admin.site.register(Emotion, Emotion_Admin)
