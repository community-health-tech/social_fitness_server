from dateutil import parser
from django.http import Http404
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from fitness.models import DATE_DELTA_1D, DATE_DELTA_7D
from fitness.models import GroupFitnessFactory, PersonFitnessFactory
from fitness.serializers import GroupFitnessSerializer, PersonFitnessSerializer
from fitness_connector.activity import PersonActivity
from people.models import Person, Group, Membership


# CLASSES
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


# CLASSES FOR ADMIN VIEW (CURRENTLY UNUSED)
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
