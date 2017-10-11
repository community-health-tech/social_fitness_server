from django.contrib import admin
from challenges.models import LevelGroup, Level, GroupChallenge, \
    PersonChallenge, PersonFitnessMilestone

# Register your models here.
admin.site.register(LevelGroup)
admin.site.register(Level)
admin.site.register(GroupChallenge)
admin.site.register(PersonChallenge)
admin.site.register(PersonFitnessMilestone)