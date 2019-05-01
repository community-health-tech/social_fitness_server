from django.contrib import admin
from .models import Person
from .models import Group, Membership
from .models import Circle, CircleMembership

# Register your models here.
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'internal_name', 'user')
    list_display_links = ('name', 'internal_name')
    search_fields = ['name', 'internal_name', 'user__username']


admin.site.register(Person, PersonAdmin)

admin.site.register(Group)

admin.site.register(Circle)


class MembershipAdmin(admin.ModelAdmin):
    list_display = ('person', 'role', 'group')
    list_display_links = ('person', 'role', 'group')
    search_fields = ['group__name', 'person__name']


admin.site.register(Membership, MembershipAdmin)


class CircleMembershipAdmin(admin.ModelAdmin):
    list_display = ('person', 'circle')
    list_display_links = ('person', 'circle')
    search_fields = ['circle__name', 'person__name']


admin.site.register(CircleMembership, CircleMembershipAdmin)

