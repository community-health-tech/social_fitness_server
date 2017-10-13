from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from challenges.classes import ListOfAvailableChallenges, CurrentChallenge
from challenges.models import GroupChallenge
from challenges.serializers import ListOfAvailableChallengestSerializer, AvailableChallengeSerializer, \
    CurrentChallengeSerializer
from fitness.models import DATE_DELTA_7D, DATE_DELTA_1D
from people import helpers as people_helper


class Available(APIView):
    """
    List all available challenges that a family can pick.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        group = people_helper.get_group(request.user.id)
        if GroupChallenge.is_there_a_running_challenge(group) :
            output = {"message": "There is a running challenge"}
            return Response(output, status.HTTP_400_BAD_REQUEST)

        challenges = ListOfAvailableChallenges(group)
        serializer = ListOfAvailableChallengestSerializer(challenges)
        return Response(serializer.data)


class Create(APIView):
    """
    Create new challenges uniformly for all group members
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        group = people_helper.get_group(request.user.id)
        if GroupChallenge.is_there_a_running_challenge(group) :
            output = {"message": "There is a running challenge"}
            return Response(output, status.HTTP_400_BAD_REQUEST)

        validator = AvailableChallengeSerializer(data=request.data)
        if validator.is_valid():
            challenge = GroupChallenge.create_from_data(group, validator.validated_data)
            current_challenge = CurrentChallenge(challenge, is_new=True)
            serializer = CurrentChallengeSerializer(current_challenge)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)


    def __get_end_date(self, start_datetime, data):
        total_duration = data['total_duration']
        if total_duration == "1d" :
            return start_datetime + DATE_DELTA_1D
        elif total_duration == "7d" :
            return start_datetime + DATE_DELTA_7D


class Current(APIView):
    """
    List current challenges that has been selected by a Group
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        group = people_helper.get_group(request.user.id)
        if GroupChallenge.is_there_a_running_challenge(group) == False:
            output = {"message": "There is no running challenge"}
            return Response(output, status.HTTP_400_BAD_REQUEST)

        challenge = GroupChallenge.objects.filter(group=group).latest()
        current_challenge = CurrentChallenge(challenge)
        serializer = CurrentChallengeSerializer(current_challenge)
        return Response(serializer.data)