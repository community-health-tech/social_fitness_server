from django.db import models
from people.models import Group


GROUPSTORY_ADMIN_STRING = "{0} \t\treading '{1}' \t\t\t\t({2})"


# Models
class Category(models.Model):
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=2)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Story(models.Model):
    MEMBERSHIP_STRING = "{0} ({1})"

    title = models.CharField(max_length=50)
    cover_url = models.URLField(max_length=200)
    def_url = models.URLField(max_length=200)
    slug = models.SlugField(max_length=25)
    is_locked = models.BooleanField(default=False)
    category = models.ForeignKey(Category, null=True, blank=True, default=None,
                                   on_delete=models.SET_NULL)
    next_story = models.ForeignKey('self', null=True, blank=True, default=None,
                                   on_delete=models.SET_NULL)

    class Meta:
        verbose_name_plural = "stories"

    def __str__(self):
        if self.category:
            category_name = self.category.name
        else:
            category_name = "Uncategorized"
        return Story.MEMBERSHIP_STRING.format(self.title, category_name)


class GroupStory(models.Model):
    group = models.ForeignKey(Group)
    story = models.ForeignKey(Story)
    is_current = models.BooleanField()
    current_page = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "group stories"

    def __str__(self):
        if self.category:
            category_name = self.story.category.short_name
        else:
            category_name = "Uncategorized"
        return GROUPSTORY_ADMIN_STRING.format(self.group.name, self.story.title, category_name)


# Standard Classes

class GroupStoryList():

    def __init__(self, stories, current_story_id):
        self.stories = stories
        self.current_story_id = current_story_id
