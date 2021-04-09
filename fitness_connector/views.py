from django.http import HttpResponse
from rest_framework.response import Response
from fitness_connector import authenticate as fitbit_authenticate
from fitness_connector.activity import PersonActivity
from fitness_connector.classes import PersonFitnessSyncResult
from fitness_connector.serializers import PersonFitnessSyncResultSerializer


# Views
def index(request):
    return HttpResponse("Hello, people.")

def connect(request, person_id):
    return HttpResponse(fitbit_authenticate.get_auth_url())

def authorize(request):
    code = request.GET.get('code')
    return HttpResponse(fitbit_authenticate.authenticate(code))
    
def update (request, person_id):
    person_activity = PersonActivity(person_id)
    #last_sync_time = person_activity.pull_recent_data()
    #person_fitness_sync = PersonFitnessSyncResult(person_id, last_sync_time)
    #serializer = PersonFitnessSyncResultSerializer(person_fitness_sync)
    #return Response(serializer.data)
    return HttpResponse(person_activity.pull_recent_data())