from django.contrib import admin
from story_manager.models import Category, Story, GroupStory


admin.site.register(Category)
admin.site.register(GroupStory)


class StoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'category')
    list_display_links = ('title',)
    list_filter = ('category__name',)
    ordering = ('category__id', 'order')


admin.site.register(Story, StoryAdmin)