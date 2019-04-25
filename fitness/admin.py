from django.contrib import admin
from .models import ActivityByMinute, ActivityByDay

# Register your models here.

class ActivityByDayAdmin(admin.ModelAdmin):
    list_display = ('person', 'date', 'steps', 'calories', 'distance')
    list_display_links = ('person', 'date', 'steps', 'calories', 'distance')
    search_fields = ['person__name']


admin.site.register(ActivityByDay, ActivityByDayAdmin)


class ActivityByMinuteAdmin(admin.ModelAdmin):
    list_display = ('person', 'date', 'time', 'steps', 'calories', 'distance')
    list_display_links = ('person', 'date', 'time', 'steps', 'calories', 'distance')
    search_fields = ['person__name']


admin.site.register(ActivityByMinute, ActivityByMinuteAdmin)
