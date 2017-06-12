from django.conf.urls import url
from . import views

urlpatterns = [
    # ex: /fitbit/oauth/5
    url(r'^oauth/(?P<person_id>[0-9]+)/$', views.connect, name='connect'),
    # ex: /fitbit/oauth/authorize/?code=dhshfksduhfsdjfh
    url(r'^oauth/authorize/$', views.authorize, name='authorize'),
    # ex: /fitbit/update/person
    url(r'^update/person/(?P<person_id>[0-9]+)/$', views.update, name='update'),
]