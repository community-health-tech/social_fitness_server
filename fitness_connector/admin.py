from django.contrib import admin
from .models import Account

# Register your models here.
class AccountAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'person', 'last_pull_time', 'device_version', 'expires_at')
    list_display_links = ('fullname', 'person',)
    search_fields = ['fullname', 'user_id', 'person__name']


admin.site.register(Account, AccountAdmin)
