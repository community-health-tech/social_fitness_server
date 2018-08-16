from typing import List, Set, Dict, Tuple, Text, Optional

from datetime import date, timedelta

from django.db import models
from fitness_connector.models import Account
from people.models import Person, Group, Membership


# CONSTANTS
DATE_DELTA_1D = timedelta(days=1)
DATE_DELTA_7D = timedelta(days=7)
STAGE_PRECONTEMPLATIVE = 1
STAGE_CONTEMPLATIVE = 2
STAGE_PREPARATION = 3
STAGE_ACTION = 4
STAGE_MAINTENANCE = 5
STAGES = (
    (STAGE_PRECONTEMPLATIVE, "Precontemplative"),
    (STAGE_CONTEMPLATIVE, "Contemplative"),
    (STAGE_PREPARATION, "Preparation"),
    (STAGE_ACTION, "Action"),
    (STAGE_MAINTENANCE, "Maintenance")
)

ACTIVITY_BYMINS_STRING = "{0} on {1} {2}"
ACTIVITY_BYDAY_STRING = "{0} on {1}"
    

# Django Models
class ActivityByMinute(models.Model):
    """A Person's activity on minute-by-minute basis"""
    #date_time = models.DateTimeField()
    date = models.DateField()
    time = models.TimeField()
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    steps = models.IntegerField()
    calories = models.FloatField()
    level = models.IntegerField()
    distance = models.FloatField()
    
    def __str__(self):
        return ACTIVITY_BYMINS_STRING.format(self.person.name,
                                             self.date,
                                             self.time)


class ActivityByDay(models.Model):
    """A Person's activity information per day"""
    date = models.DateField()
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    steps = models.IntegerField()
    calories = models.FloatField()
    active_minutes = models.IntegerField()
    distance = models.FloatField()

    def __str__(self):
        return ACTIVITY_BYDAY_STRING.format(self.person.name, self.date)


# Standard Classes
class PersonFitness:
    """
    Describes a Person's Fitness
    """

    def __init__(self, person_id, activities, role=None):
        person = Person.objects.get(pk=person_id)
        account = Account.objects.get(person__pk=person_id)
        self.id = person_id  # type: int
        self.name = person.name  # type: str
        self.last_pull_time = account.last_pull_time
        self.activities = activities  # type: List[ActivityByDay]
        self.role = role  # type: str


class GroupFitness:
    """
    Describes every Person's Fitness in a Group group_id
    """

    def __init__(self, group_id, activities):
        group = Group.objects.get(pk=group_id)
        self.id = group.id  # type: int
        self.name = group.name  # type: str
        self.activities = activities  # type: List[PersonFitness]


# Factory Classes
class PersonFitnessFactory:
    """
    Factory class to produce a PersonFitness
    """

    @staticmethod
    def get(person_id, start_date, end_date, role):
        # type: (int, date, date, str) -> PersonFitness
        """
        :return: PersonFitness between start_date to end_date
        """
        daily_activities = ActivityByDay.objects \
            .filter(date__gte=start_date) \
            .filter(date__lte=end_date) \
            .filter(person_id__exact=person_id) \
            .only("date", "steps", "calories", "distance")
        return PersonFitness(person_id, daily_activities, role)

    @staticmethod
    def get_one_day(person_id, this_date, role):
        # type: (int, date, str) -> PersonFitness
        """
        :return: PersonFitness on this_date
        """
        activity = ActivityByDay.objects\
            .filter(date__exact=this_date)\
            .filter(person_id__exact=person_id)\
            .only("date", "steps", "calories", "distance")
        return PersonFitness(person_id, activity, role)


class GroupFitnessFactory:
    """
    Factory class to produce a GroupFitness
    """

    @staticmethod
    def get(group_id, start_date, end_date):
        # type: (int, date, date) -> GroupFitness
        """
        :return: GroupFitness between start_date to end_date
        """
        member_activities = []
        for membership in Membership.objects.filter(group=group_id):
            member_activities.append(PersonFitnessFactory.get(
                membership.person.id,
                start_date,
                end_date,
                membership.role))
        return GroupFitness(group_id, member_activities)