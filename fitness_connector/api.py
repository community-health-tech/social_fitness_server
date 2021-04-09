import time
from django.http import Http404
from fitbit import Fitbit
from oauthlib.oauth2 import InvalidGrantError, TokenExpiredError
from rest_framework.response import Response
from rest_framework.views import APIView

from fitness_connector.activity import PersonActivity
from fitness_connector.classes import PersonFitnessSyncResult
from fitness_connector.models import Account
from fitness_connector.serializers import PersonFitnessSyncResultSerializer
from people.models import Person


SECONDS_BEFORE_NEXT_SYNC = 2  # type: int
SECONDS_BEFORE_NEXT_TOKEN_REFRESH = 0.1  # type: float

# CLASSES
class PersonFitnessDataSync(APIView):
    """
    Download the latest fitness data of the person id
    """

    def get(self, request, person_id, format=None):
        person_activity = get_person_activity(person_id)
        last_sync_time = person_activity.pull_recent_data()
        person_fitness_sync = PersonFitnessSyncResult(person_id, last_sync_time)
        serializer = PersonFitnessSyncResultSerializer(person_fitness_sync)
        return Response(serializer.data)


class AllUsersFitnessDataSync(APIView):

    def get (self, request, format=None):
        all_people_with_account = Account.objects.all()

        sync_results = dict()  # type: dict

        for account in all_people_with_account:
            person_activity = PersonActivity(account.person.id)
            last_sync_time = self.__try_pull_recent_data(person_activity)
            sync_results[str(person_activity.person_id)] = last_sync_time
            time.sleep(SECONDS_BEFORE_NEXT_SYNC)

        return Response(sync_results)

    def __try_pull_recent_data(self, person_activity):
        # type: (PersonActivity) -> str
        try:
            return person_activity.pull_recent_data()
        except TokenExpiredError:
            return "TokenExpiredError"
        except InvalidGrantError:
            return "InvalidGrantError"


class RefreshAllToken(APIView):

    def get (self, request, format=None):
        all_people_with_account = Account.objects.all()

        refresh_results = dict()  # type: dict

        for account in all_people_with_account:
            person_activity = PersonActivity(account.person.id)
            refresh_results[str(account.person.id)] = {
                "person_name": account.person.name,
                "expires_at": person_activity.account.expires_at,
                "last_pull_time": person_activity.account.last_pull_time,
            }

            time.sleep(SECONDS_BEFORE_NEXT_TOKEN_REFRESH)

        return Response(refresh_results)



# HELPER METHODS
def get_person_activity(person_id):
    if Person.objects.filter(id=person_id).exists() == False:
        raise Http404
    elif Account.objects.filter(person_id=person_id).exists() == False:
        raise Http404
    else:
        return PersonActivity(person_id)