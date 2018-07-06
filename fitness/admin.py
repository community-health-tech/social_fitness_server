from django.contrib import admin
from .models import ActivityByMinute, ActivityByDay

# Register your models here.
admin.site.register(ActivityByMinute, ActivityByDay)
