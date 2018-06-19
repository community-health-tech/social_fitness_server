from django.contrib import admin
from .models import Person
from .models import Group, Membership
from .models import Circle, CircleMembership

# Register your models here.
admin.site.register(Person)
admin.site.register(Group)
admin.site.register(Membership)
admin.site.register(Circle)
admin.site.register(CircleMembership)

