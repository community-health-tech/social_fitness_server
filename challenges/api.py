from django.http import Http404
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from challenges.models import AvailableChallenges
from challenges.serializers import AvailableChallengesSerializer
from people.models import Person, Group


class Available(APIView):
    """
    Get a list of available challenges
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        group = ChallengeHelper.get_group(request.user.id)
        available_challenges = AvailableChallenges(group)
        serializer = AvailableChallengesSerializer(available_challenges)

        return Response(serializer.data)


# HELPER CLASSES
class ChallengeHelper():

    @staticmethod
    def get_group(user_id):
        try:
            person = Person.objects.get(user__id=user_id)
            return Group.objects.get(members=person)
        except Person.DoesNotExist:
            raise Http404
        except Group.DoesNotExist:
            raise Http404