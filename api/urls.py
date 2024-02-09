from django.urls import path, re_path, include
from rest_framework.urlpatterns import format_suffix_patterns

from api.views import FirebaseToken
from challenges.api import Challenges, ChallengeCompletion, Create, \
    IndividualizedChallenges, IndividualizedChallengesCustomSteps
from fitness.api import UserGroupActivities
from fitness_connector.api import PersonFitnessDataSync, \
    AllUsersFitnessDataSync, RefreshAllToken
from people.api import UserInfo, UserGroupInfo, UserCircleInfo, PersonInfo, \
    PersonProfileInfo, UserCircleListInfo
from story_manager.api import UserStory, UserStoryList

urlpatterns = [
    # REST FRAMEWORK
    # User Authentication
    path(r'', include('rest_framework.urls', namespace='rest_framework')),

    # LOGGED USER'S VIEWS
    # Logged User's details
    path(r'^user/$', UserInfo.as_view()),

    # Logged User's Person info
    path(r'^person/info/$', UserInfo.as_view()),
    re_path(r'^person/(?P<person_id>[0-9]+|-)/$', PersonInfo.as_view()),

    # Logged User's: Get and set a person's metadata
    re_path(r'^person/(?P<person_id>[0-9]+)/meta/profile/$', PersonProfileInfo.as_view()),

    # Logged Family's details
    path(r'^group/info/$', UserGroupInfo.as_view()),

    # Logged Family's circle
    re_path(r'^circle/(?P<circle_id>[0-9]+)/$', UserCircleInfo.as_view()),
    path(r'^circle/all/$', UserCircleListInfo.as_view()),

    # Logged Family's Activities in 7 days
    re_path(r'^group/activities/7d/'
        r'(?P<start_date_string>\d{4}-\d{2}-\d{2})$',
        UserGroupActivities.as_view()),

    # Logged Family's: All Stories
    path(r'^group/stories/all$', UserStoryList.as_view()),

    # Logged Family's: Specific Story
    re_path(r'^group/stories/(?P<story_id>[0-9]+)/$', UserStory.as_view()),

    # Logged Family's: Challenges
    path(r'^group/challenges$', Challenges.as_view()),

    # Logged Family's: Challenges with average set by the user
    re_path(r'^group/challenges/steps_average/(?P<steps_average>\d+)/$', Challenges.as_view()),

    # Logged Family's: create a new challenge from available challenges
    path(r'^group/challenges/create$', Create.as_view()),

    # Logged Family's: Complete the currently running challenges
    path(r'^group/challenges/set_completed$', ChallengeCompletion.as_view()),
    re_path(r'^group/challenges/set_completed/(?P<override>[\w-]+)/$', ChallengeCompletion.as_view()),

    # Logged Family's: Individualized challenges
    path(r'^group/challenges/individualized$',
        IndividualizedChallenges.as_view()),
    path(r'^group/challenges/individualized/steps_average$',
        IndividualizedChallengesCustomSteps.as_view()),
    path(r'^group/challenges/individualized/set_completed$',
        ChallengeCompletion.as_view()),
    re_path(r'^group/challenges/individualized/set_completed/(?P<override>[\w-]+)/$',
        ChallengeCompletion.as_view()),

    # Sync the fitbit data of the person
    # url(r'^fitbit/update/person/(?P<person_id>[0-9]+)/$', fitness_connector_views.update, name='update'),
    re_path(r'^fitbit/update/person/(?P<person_id>[0-9]+)/$', PersonFitnessDataSync.as_view()),
    path(r'^fitbit/update/all$', AllUsersFitnessDataSync.as_view()),
    path(r'^fitbit/token/update/all$', RefreshAllToken.as_view()),

    # Logged Family's: Challenges
    # url(r'^group/challenges2$', Challenges.as_view()),

    # Logged Family's: all challenges that can be selected
    # url(r'^group/challenges/available$', Available.as_view()),

    # Logged Family's: create a new challenge from available challenges
    # url(r'^group/challenges/create$', Create.as_view()),

    # Logged Family's: create a new challenge from available challenges
    # url(r'^group/challenges/current$', Current.as_view()),

    # Logged Family's: get a Firebase token
    path(r'^firebase/get_token$', FirebaseToken.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)


    #
    # # ADMIN VIEWS
    # # People list
    # url(r'^people/$', views.PersonList.as_view()),
    # url(r'^person/list/$', views.PersonList.as_view()),
    #
    # # Person's details
    # url(r'^person/(?P<person_id>[0-9]+)/$', views.PersonInfo.as_view()),
    #
    # # Family list
    # url(r'^groups/$', views.GroupList.as_view()),
    # url(r'^group/list/$', views.GroupList.as_view()),
    #
    # # Family's details
    # url(r'^group/(?P<group_id>[0-9]+)/$', views.GroupInfo.as_view()),
    #
    # # Person's Activities in one day
    # # Eg: /fitbit/activity/person/1/1d/2017-05-28/
    # url(r'^person/(?P<person_id>[0-9]+)/activities/1d/'
    #     r'(?P<date_string>\d{4}-\d{2}-\d{2})$',
    #     views.Person1DActivity.as_view()),
    #
    # # Person's Activities in 7 days
    # # Eg: /fitbit/activity/person/1/7d/2017-05-28/
    # url(r'^person/(?P<person_id>[0-9]+)/activities/7d/'
    #     r'(?P<start_date_string>\d{4}-\d{2}-\d{2})$',
    #     views.PersonActivities.as_view()),
    #
    # # Group activities in 7 days. I.e. /group/{group_id}/activities/7d/{start_date}
    # # Eg: /group/1/activities/7d/2017-05-28/
    # url(r'^group/(?P<group_id>[0-9]+)/activities/7d/'
    #     r'(?P<start_date_string>\d{4}-\d{2}-\d{2})$',
    #     views.GroupActivities.as_view()),
    #
    # # Group activities in 7 days. I.e. /family/{group_id}/activities/7d/{start_date}
    # # Eg: /family/1/activities/7d/2017-05-28/
    # url(r'^family/(?P<family_id>[0-9]+)/activities/7d/'
    #     r'(?P<start_date_string>\d{4}-\d{2}-\d{2})$',
    #     views.PeopleActivities.as_view()),