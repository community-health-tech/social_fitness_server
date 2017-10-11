from django.http import Http404
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from people.models import Person, Group
from story_manager.models import GroupStory, GroupStoryList
from story_manager.serializers import GroupStorySerializer, \
    GroupStoryListSerializer


class UserStoryList(APIView):
    """
    Retrieve the stories that can be read by the Group in which the logged
    user belongs to
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        group = StoryHelper.get_group(request.user.id)
        group_stories = GroupStory.objects.filter(group=group)
        current_story_id = UserStoryList.get_current_story_id(group_stories)

        group_story_list = GroupStoryList(group_stories, current_story_id)
        serializer = GroupStoryListSerializer(group_story_list)

        return Response(serializer.data)

    @staticmethod
    def get_current_story_id(group_stories):
        for group_story in group_stories:
            if group_story.is_current:
                return group_story.story.id
        return None


class UserStory(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, story_id, format=None):
        group = StoryHelper.get_group(request.user.id)
        group_story = StoryHelper.get_group_story(group, story_id)
        serializer = GroupStorySerializer(group_story)
        return Response(serializer.data)

    def put(self, request, story_id, format=None):
        group = StoryHelper.get_group(request.user.id)
        group_story = StoryHelper.get_group_story(group, story_id)
        serializer = GroupStorySerializer(group_story, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.data)


class StoryHelper():

    @staticmethod
    def get_group(user_id):
        try:
            person = Person.objects.get(user__id=user_id)
            return Group.objects.get(members=person)
        except Person.DoesNotExist:
            raise Http404
        except Group.DoesNotExist:
            raise Http404

    @staticmethod
    def get_group_story(group, story_id):
        try:
            eligible_story = GroupStory.objects.filter(group=group) \
                .get(story_id__exact=story_id)
            return eligible_story
        except GroupStory.DoesNotExist:
            raise Http404


