from datetime import timedelta
from dateutil import parser
from django.http import Http404
from people.models import Person, Group, Membership
from people.serializers import PersonSerializer, GroupSerializer, GroupListSerializer
from fitness_connector.activity import PersonActivity
from fitness.models import PersonFitnessFactory
from fitness.serializers import PersonFitnessSerializer, PeopleFitnessSerializer
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response


# Constants
DATE_DELTA_1D = timedelta(days=1)
DATE_DELTA_7D = timedelta(days=7)


class PersonList(generics.ListAPIView):
    """
    List all Persons
    """
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


class PersonInfo(APIView):
    """
    Retrieve a Person's detailed information
    """

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



class PersonList(generics.ListAPIView):
    """
    List all Persons
    """
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


class PersonInfo(APIView):
    """
    Retrieve a Person's detailed information
    """

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


class FamilyList(generics.ListAPIView):
    """
    List all Families
    """
    queryset = Group.objects.all()
    serializer_class = GroupListSerializer


class FamilyInfo(APIView):
    """
    Retrieve a Family's detailed information
    """

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
    Retrieve a person's detail and their activities in one day
    """

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
    """""Retrieve all people's details and their activities"""

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


    
"""
from people.models import Person
from people.serializers import PersonSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class PersonList(APIView):
    def get(self, request, format=None):
        snippets = Person.objects.all()
        serializer = PersonSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = PersonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class PersonDetail(APIView):

    def get_object(self, pk):
        try:
            return Person.objects.get(pk=pk)
        except Person.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        person = self.get_object(pk)
        serializer = PersonSerializer(person)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        person = self.get_object(pk)
        serializer = PersonSerializer(person, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        person = self.get_object(pk)
        person.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        

"""