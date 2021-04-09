from django.contrib import admin
from challenges.models import LevelGroup, Level, GroupChallenge, \
    PersonChallenge, PersonFitnessMilestone

# Register your models here.
admin.site.register(LevelGroup)
admin.site.register(Level)
admin.site.register(PersonFitnessMilestone)


class GroupChallengeAdmin(admin.ModelAdmin):
    list_display = ('group', 'duration', 'start_datetime', 'end_datetime', 'completed_datetime', 'level')
    list_display_links = ('group', 'duration')
    ordering = ('-start_datetime', '-end_datetime')
    search_fields = ['group__name']


admin.site.register(GroupChallenge, GroupChallengeAdmin)


class PersonChallengeAdmin(admin.ModelAdmin):
    list_display = ('person', 'unit_goal', 'unit', 'unit_duration', 'group_challenge', 'level')
    list_display_links = ('person', 'unit', 'unit_goal', 'unit_duration')
    search_fields = ['person__name']


admin.site.register(PersonChallenge, PersonChallengeAdmin)