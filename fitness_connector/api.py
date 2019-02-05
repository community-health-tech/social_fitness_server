# CLASSES
from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView

from fitness_connector.activity import PersonActivity
from fitness_connector.classes import PersonFitnessSyncResult
from fitness_connector.models import Account
from fitness_connector.serializers import PersonFitnessSyncResultSerializer
from people.models import Person


class PersonFitnessDataSync(APIView):
    """
    Download the latest fitness data of the person id
    """

    @staticmethod
    def __get_person_activity(person_id):
        if Person.objects.filter(id=person_id).exists() == False:
            raise Http404
        elif Account.objects.filter(person_id=person_id).exists() == False:
            raise Http404
        else:
            return PersonActivity(person_id)

    def get(self, request, person_id, format=None):
        person_activity = PersonFitnessDataSync.__get_person_activity(person_id)
        last_sync_time = person_activity.pull_recent_data()
        person_fitness_sync = PersonFitnessSyncResult(person_id, last_sync_time)
        serializer = PersonFitnessSyncResultSerializer(person_fitness_sync)
        return Response(serializer.data)
