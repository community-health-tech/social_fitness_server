from django.http import HttpResponse
from fitness_connector import authenticate as fitbit_authenticate
from fitness_connector.activity import PersonActivity


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
    return HttpResponse(person_activity.pull_recent_data())