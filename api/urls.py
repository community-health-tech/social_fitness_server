from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views


urlpatterns = [
    # People list
    url(r'^people/$', views.PersonList.as_view()),
    url(r'^person/list/$', views.PersonList.as_view()),

    # Person's details
    url(r'^person/(?P<person_id>[0-9]+)/$', views.PersonInfo.as_view()),

    # Family list
    url(r'^families/$', views.FamilyList.as_view()),
    url(r'^family/list/$', views.FamilyList.as_view()),

    # Family's details
    url(r'^family/(?P<group_id>[0-9]+)/$', views.FamilyInfo.as_view()),

    # Person's Activities in one day
    # Eg: /fitbit/activity/person/1/1d/2017-05-28/
    url(r'^person/(?P<person_id>[0-9]+)/activities/1d/'
        r'(?P<date_string>\d{4}-\d{2}-\d{2})$',
        views.Person1DActivity.as_view()),

    # Person's Activities in 7 days
    # Eg: /fitbit/activity/person/1/7d/2017-05-28/
    url(r'^person/(?P<person_id>[0-9]+)/activities/7d/'
        r'(?P<start_date_string>\d{4}-\d{2}-\d{2})$',

        views.PersonActivities.as_view()),

        #views.PersonActivities.as_view()),

    # Group activities in 7 days. I.e. /family/{group_id}/activities/7d/{start_date}
    # Eg: /family/1/activities/7d/2017-05-28/
    url(r'^family/(?P<family_id>[0-9]+)/activities/7d/'
        r'(?P<start_date_string>\d{4}-\d{2}-\d{2})$', views.PeopleActivities.as_view()),


]

urlpatterns = format_suffix_patterns(urlpatterns)