import firebase_admin
import time
from django.http import Http404
from firebase_admin import auth
from firebase_admin import credentials
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from people.models import Person, Group

ONE_HOUR_IN_SECONDS = 60 * 60
CRED_PATH = '../cred/wellness-storytelling-firebase-adminsdk-osfs2-eca160348c.json'

class FirebaseToken(APIView):
    """
    Retrieve current User's token to use Firebase. The token will expire after
    one hour.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def __init__(self):
        self.cred = credentials.Certificate(CRED_PATH)

    def get(self, request, format=None):
        self.fb_app = firebase_admin.initialize_app(self.cred)
        uid = self.__get_uid(request.user.id)
        auth_response = {
            "token": auth.create_custom_token(uid),
            "expiredAtTimestamp": int(time.time()) + ONE_HOUR_IN_SECONDS
        }
        return Response(auth_response)

    def __get_uid(self, user_id):
        # type: (str) -> str
        try:
            person = Person.objects.get(user__id=user_id)
            group = Group.objects.get(members=person)
            return group.name
        except Person.DoesNotExist:
            raise Http404
        except Group.DoesNotExist:
            raise Http404
