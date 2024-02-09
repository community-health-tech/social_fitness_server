from django.urls import path, re_path
from . import views

urlpatterns = [
    # ex: /fitbit/oauth/5
    re_path(r'^oauth/(?P<person_id>[0-9]+)/$', views.connect, name='connect'),
    # ex: /fitbit/oauth/authorize/?code=dhshfksduhfsdjfh
    path(r'^oauth/authorize/$', views.authorize, name='authorize'),
    # ex: /fitbit/update/person
    re_path(r'^update/person/(?P<person_id>[0-9]+)/$', views.update, name='update'),
]