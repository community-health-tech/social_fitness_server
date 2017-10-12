from django.http import Http404
from rest_framework import permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response

from people.models import Person, Group
from people.serializers import PersonSerializer, GroupSerializer, \
    GroupListSerializer
from fitness_connector.activity import PersonActivity


# CLASSES
class UserInfo(APIView):
    """
    Retrieve current User's detailed information
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, user_id):
        try:
            return Person.objects.get(user__id=user_id)
        except Person.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        person = self.get_object(request.user.id)
        serializer = PersonSerializer(person)
        return Response(serializer.data)


class UserGroupInfo(APIView):
    """
    Retrieve the Group's detailed information in which the logged User
    belongs to
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_person(self, user_id):
        try:
            return Person.objects.get(user__id=user_id)
        except Person.DoesNotExist:
            raise Http404

    def get_group(self, person):
        try:
            return Group.objects.get(members=person)
        except Group.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        person = self.get_person(request.user.id)
        group = self.get_group(person)
        serializer = GroupSerializer(group)

        return Response(serializer.data)


# CLASSES FOR ADMIN VIEWS (CURRENTLY NOT USED)
class PersonList(generics.ListAPIView):
    """
    List all Persons
    """
    permission_classes = (permissions.IsAdminUser,)
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


class PersonInfo(APIView):
    """
    Retrieve a Person's detailed information
    """
    permission_classes = (permissions.IsAdminUser,)

    def get_object(self, person_id):
        try:
            return Person.objects.get(pk=person_id)
        except Person.DoesNotExist:
            raise Http404

    def get(self, request, person_id, format=None):
        person = self.get_object(person_id)
        person_activity = PersonActivity(person_id)
        response = {
            'person': {
                'person_id': person_id,
                'name': person.name,
                'last_pull_time': person_activity.account.last_pull_time
            }
        }

        return Response(response)


class GroupList(generics.ListAPIView):
    """
    List all Families
    """
    permission_classes = (permissions.IsAdminUser,)
    queryset = Group.objects.all()
    serializer_class = GroupListSerializer


class GroupInfo(APIView):
    """
    Retrieve a Group's detailed information
    """
    permission_classes = (permissions.IsAdminUser,)

    def get_object(self, group_id):
        try:
            return Group.objects.get(pk=group_id)
        except Group.DoesNotExist:
            raise Http404

    def get(self, request, group_id, format=None):
        group = self.get_object(group_id)
        serializer = GroupSerializer(group)

        return Response(serializer.data)


