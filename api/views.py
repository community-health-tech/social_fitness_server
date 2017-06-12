from datetime import timedelta
from dateutil import parser
from django.http import Http404
from people.models import Person, Group, Membership
from people.serializers import PersonSerializer, GroupSerializer, \
    GroupListSerializer
from fitness_connector.activity import PersonActivity
from fitness.models import PersonFitnessFactory, GroupFitnessFactory
from fitness.serializers import PersonFitnessSerializer, \
    GroupFitnessSerializer
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions


# Constants
DATE_DELTA_1D = timedelta(days=1)
DATE_DELTA_7D = timedelta(days=7)


# === Admin Only Views ===================================================== #


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


class Person1DActivity(APIView):
    """
    Retrieve a Person's detailed information and their activities in one day
    """

    permission_classes = (permissions.IsAdminUser,)

    def get_object(self, person_id):
        try:
            return Person.objects.get(pk=person_id)
        except Person.DoesNotExist:
            raise Http404

    def get(self, request, person_id, date_string, format=None):
        person = self.get_object(person_id)
        start_date = parser.parse(date_string)
        person_fitness = PersonFitnessFactory.get_one_day(person.id, start_date)
        serializer = PersonFitnessSerializer(person_fitness)

        return Response(serializer.data)


class PersonActivities(APIView):
    """
    Retrieve a person's detail and their activities
    """

    permission_classes = (permissions.IsAdminUser,)

    def get_object(self, person_id):
        try:
            return Person.objects.get(pk=person_id)
        except Person.DoesNotExist:
            raise Http404

    def get(self, request, person_id, start_date_string, format=None):
        person = self.get_object(person_id)
        start_date = parser.parse(start_date_string)
        end_date = start_date + DATE_DELTA_7D
        person_fitness = PersonFitnessFactory.get(person.id,
                                                  start_date,
                                                  end_date)
        serializer = PersonFitnessSerializer(person_fitness)

        return Response(serializer.data)


class PeopleActivities(APIView):
    """Retrieve all people's details and their activities"""

    permission_classes = (permissions.IsAdminUser,)

    def get_object(self, person_id):
        try:
            return Person.objects.all()
        except Person.DoesNotExist:
            raise Http404


    def get(self, request, family_id, start_date_string, format=None):
        start_date = parser.parse(start_date_string)
        end_date = start_date + DATE_DELTA_7D
        members = []

        group = Group.objects.get(pk=family_id)
        for person in group.members.all():
            person_activity = PersonActivity(person.id)
            person_fitness = PersonFitnessFactory.get(person.id,
                                                      start_date,
                                                      end_date)
            serializer = PersonFitnessSerializer(person_fitness)
            membership = Membership.objects.get(pk=person.id)
            response = {
                'person': {
                    'person_id': person.id,
                    'name': person.name,
                    'last_pull_time': person_activity.account.last_pull_time,
                    'role': membership.role

                },
                'activities': serializer.data["activities"]
            }

            members.append(response)

        return Response(members)


class GroupActivities(APIView):
    """
    Retrieve the activities of all Persons in the Group in which the logged User
    belongs to
    """

    permission_classes = (permissions.IsAdminUser,)

    def get_group(self, group_id):
        try:
            return Group.objects.get(pk=group_id)
        except Group.DoesNotExist:
            raise Http404

    def get(self, request, group_id, start_date_string, format=None):
        group = self.get_group(group_id)
        start_date = parser.parse(start_date_string)
        end_date = start_date + DATE_DELTA_7D
        group_activities = GroupFitnessFactory.get(group.id,
                                                  start_date,
                                                  end_date)
        serializer = GroupFitnessSerializer(group_activities)
        return Response(serializer.data)


# === Logged User's Views ================================================== #


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


class UserGroupActivities(APIView):
    """
    Retrieve the activities of all Persons in the Group in which the logged User
    belongs to
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

    def get(self, request, start_date_string, format=None):
        group = self.get_group(request.user.id)
        start_date = parser.parse(start_date_string)
        end_date = start_date + DATE_DELTA_7D
        group_activities = GroupFitnessFactory.get(group.id,
                                                  start_date,
                                                  end_date)
        serializer = GroupFitnessSerializer(group_activities)
        return Response(serializer.data)
