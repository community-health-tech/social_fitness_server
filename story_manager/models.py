from django.db import models
from people.models import Group


GROUPSTORY_ADMIN_STRING = "{0} reading '{1}'"


# Models

class Story(models.Model):
    title = models.CharField(max_length=50)
    cover_url = models.URLField(max_length=200)
    def_url = models.URLField(max_length=200)
    slug = models.SlugField(max_length=25)

    class Meta:
        verbose_name_plural = "stories"

    def __str__(self):
        return self.title


class GroupStory(models.Model):
    group = models.ForeignKey(Group)
    story = models.ForeignKey(Story)
    is_current = models.BooleanField()
    current_page = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "group stories"

    def __str__(self):
        return GROUPSTORY_ADMIN_STRING.format(self.group.name, self.story.title)


# Standard Classes

class GroupStoryList():

    def __init__(self, stories, current_story_id):
        self.stories = stories
        self.current_story_id = current_story_id
