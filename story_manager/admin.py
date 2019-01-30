from django.contrib import admin
from story_manager.models import Category, Story, GroupStory


admin.site.register(Category)
admin.site.register(Story)
admin.site.register(GroupStory)