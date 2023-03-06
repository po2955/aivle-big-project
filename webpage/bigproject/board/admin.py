from django.contrib import admin

# Register your models here.
from .models import Notice,Reply

class NoticeAdmin(admin.ModelAdmin):
    search_fields = ['subject']

admin.site.register(Notice,NoticeAdmin)
admin.site.register(Reply)