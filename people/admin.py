from django.contrib import admin
from .models import Person
from .models import Group
from .models import Membership

# Register your models here.
admin.site.register(Person)
admin.site.register(Group)
admin.site.register(Membership)

