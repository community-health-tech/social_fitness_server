from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from api import views
from story_manager import api as story_api


urlpatterns = [
    # User Authentication
    url(r'', include('rest_framework.urls', namespace='rest_framework')),

    # LOGGED USER'S VIEWS
    # Logged User's details
    url(r'^person/info/$', views.UserInfo.as_view()),

    # Logged Family's details
    url(r'^group/info/', views.UserGroupInfo.as_view()),

    # Logged Family's Activities in 7 days
    url(r'^group/activities/7d/(?P<start_date_string>\d{4}-\d{2}-\d{2})$',
        views.UserGroupActivities.as_view()),

    # Logged Family's Stories
    url(r'^group/stories/all$',
        story_api.UserStoryList.as_view()),

    # ADMIN VIEWS
    # People list
    url(r'^people/$', views.PersonList.as_view()),
    url(r'^person/list/$', views.PersonList.as_view()),

    # Person's details
    url(r'^person/(?P<person_id>[0-9]+)/$', views.PersonInfo.as_view()),

    # Family list
    url(r'^groups/$', views.GroupList.as_view()),
    url(r'^group/list/$', views.GroupList.as_view()),

    # Family's details
    url(r'^group/(?P<group_id>[0-9]+)/$', views.GroupInfo.as_view()),


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

    # Group activities in 7 days. I.e. /group/{group_id}/activities/7d/{start_date}
    # Eg: /group/1/activities/7d/2017-05-28/
    url(r'^group/(?P<group_id>[0-9]+)/activities/7d/'
        r'(?P<start_date_string>\d{4}-\d{2}-\d{2})$',
        views.GroupActivities.as_view()),

    # Group activities in 7 days. I.e. /family/{group_id}/activities/7d/{start_date}
    # Eg: /family/1/activities/7d/2017-05-28/
    url(r'^family/(?P<family_id>[0-9]+)/activities/7d/'
        r'(?P<start_date_string>\d{4}-\d{2}-\d{2})$',
        views.PeopleActivities.as_view()),

]

urlpatterns = format_suffix_patterns(urlpatterns)