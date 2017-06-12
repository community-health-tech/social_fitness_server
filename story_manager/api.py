from django.http import Http404
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from people.models import Person, Group
from story_manager.models import GroupStory, GroupStoryList
from story_manager.serializers import GroupStoryListSerializer


class UserStoryList(APIView):
    """
    Retrieve the stories that can be read by the Group in which the logged
    user belongs to
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get_group(self, user_id):
        try:
            person = Person.objects.get(user__id=user_id)
            return Group.objects.get(members=person)
        except Person.DoesNotExist:
            raise Http404
        except Group.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        group = self.get_group(request.user.id)
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




