from django.db import models
from fitbit.api import Fitbit
from fitness_connector.models import Account
from people.models import Person, Membership


# Constants
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
class PersonFitness():
    """
    Describes a Person's Fitness
    """

    def __init__(self, person_id, activities):
        person = Person.objects.get(pk=person_id)
        account = Account.objects.get(person__pk=person_id)
        self.id = person_id
        self.name = person.name
        self.last_pull_time = account.last_pull_time
        self.activities = activities


# Factory Classes
class PersonFitnessFactory():
    """
    Factory class to produce a PersonFitness
    """

    @staticmethod
    def get(person_id, start_date, end_date):
        """
        :return: PersonFitness between start_date to end_date
        """
        daily_activities = ActivityByDay.objects \
            .filter(date__gte=start_date) \
            .filter(date__lte=end_date) \
            .filter(person_id__exact=person_id) \
            .only("date", "steps", "calories", "distance")
        return PersonFitness(person_id, daily_activities)

    @staticmethod
    def get_one_day(person_id, this_date):
        """
        :return: PersonFitness on this_date
        """
        activity = ActivityByDay.objects\
            .filter(date__exact=this_date)\
            .filter(person_id__exact=person_id)\
            .only("date", "steps", "calories", "distance")
        return PersonFitness(person_id, activity)









