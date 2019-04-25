from django.contrib import admin
from story_manager.models import Category, Story, GroupStory


admin.site.register(Category)


class StoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'category')
    list_display_links = ('title',)
    list_filter = ('category__name',)
    ordering = ('category__id', 'order')


admin.site.register(Story, StoryAdmin)


class GroupStoryAdmin(admin.ModelAdmin):
    list_display = ('group', 'story')
    list_display_links = ('group',)
    ordering = ('group__id', 'story__order',)
    search_fields = ['group__name', 'story__title']


admin.site.register(GroupStory, GroupStoryAdmin)


