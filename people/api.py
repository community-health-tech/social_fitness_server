from django.http import Http404
from rest_framework import permissions, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request

from people.models import Person, Group, Circle, Membership, PersonMeta
from people.serializers import PersonSerializer, GroupSerializer, \
    GroupListSerializer, CircleSerializer, PersonMetaSerializer
from fitness_connector.activity import PersonActivity


# HELPER METHODS
def __get_person(user_id):
    # type: (str) -> Person
    try:
        return Person.objects.get(user__id=user_id)
    except Person.DoesNotExist:
        raise Http404

def __get_group(person):
    # type: (Person) -> Group
    try:
        return Group.objects.get(members=person)
    except Group.DoesNotExist:
        raise Http404


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


class UserCircleInfo(APIView):
    """
    Retrieve a Circle's detailed information in which the logged User
    belongs to
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_person(self, user_id):
        try:
            return Person.objects.get(user__id=user_id)
        except Person.DoesNotExist:
            raise Http404

    def get_circle(self, person, circle_id):
        try:
            return Circle.objects.get(members=person, id=circle_id)
        except Circle.DoesNotExist:
            raise Http404

    def get(self, request, circle_id, format=None):
        person = self.get_person(request.user.id)
        circle = self.get_circle(person, circle_id)
        serializer = CircleSerializer(circle)

        return Response(serializer.data)


class PersonMetaAPIView(APIView):
    """
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, user_id, format=None):
        logged_person = __get_person(request.user.id)
        group = __get_group(logged_person)
        validator = PersonMetaSerializer(data=request.data)
        if Membership.is_member(group, user_id) is False:
            output = {"message": "Can't update this person's metadata"}
            return Response(output, status=status.HTTP_401_UNAUTHORIZED)
        elif validator.is_valid():
            validated_data = validator.validated_data  # type: dict
            person = __get_person(user_id)
            PersonMetaAPIView._set_person_meta(person, validated_data)
            output = {"message": "Person's metadata has been updated"}
            return Response(output, status.HTTP_202_ACCEPTED)
        else:
            errors = validator.errors
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def _set_person_meta(person, data):
        # type: (Person, dict) -> PersonMeta
        if PersonMeta.objects.filter(person=person).exists():
            person_meta = PersonMeta.objects.filter(person=person).first()
            person_meta.profile_json = data['profile_json']
        else:
            person_meta = PersonMeta.objects.create(person=person, profile_json=data['profile_json'])
        person_meta.save()
        return person_meta


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
