from django.contrib import admin
from speach.models import Table


# Register your models here.
class SpeechAdmin(admin.ModelAdmin):
    list_display = ['speech_time',  'content', 'fluency_score', 'integrity_score',
                    'phone_score', 'tone_score', 'topic_score', 'affix_score', 'total_score']


admin.site.register(Table, SpeechAdmin)
