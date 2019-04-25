from django.contrib import admin
from .models import Person
from .models import Group, Membership
from .models import Circle, CircleMembership

# Register your models here.
admin.site.register(Person)
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

