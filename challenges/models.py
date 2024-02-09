from datetime import date, datetime
import logging

import pytz
from dateutil import parser
from django.db import models
from django.db.models import Avg
from django.utils import timezone, dateparse

from challenges import strings, constants
from people.models import Person, Group, Membership
from fitness.models import ActivityByDay, DATE_DELTA_1D, DATE_DELTA_7D, DATE_DELTA_1S

# Constants
UNIT_STEPS = "steps"
UNIT_MINUTES = "minutes"
UNIT_MINUTES_MODERATE = "minutes_moderate"
UNIT_MINUTES_VIGOROUS = "minutes_vigorous"
UNIT_DISTANCE = "distance"

# Django "Enums"
Unit = (
    (UNIT_STEPS, 'steps'),
    (UNIT_MINUTES, 'minutes'),
    (UNIT_MINUTES_MODERATE, 'minutes in moderate'),
    (UNIT_MINUTES_VIGOROUS, 'minutes in vigorous'),
    (UNIT_DISTANCE, 'distance')
)

Duration = (
    ('30m', '30 minutes'),
    ('1h', 'one hour'),
    ('2h', 'two hour'),
    ('12h', 'half-day'),
    ('1d', 'one-day'),
    ('2d', 'two-day'),
    ('3d', 'three-day'),
    ('3d', 'three-day'),
    ('7d', 'one-week')
)

DURATIONS = dict(Duration)


# Models
class LevelGroup(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class Level(models.Model):
    MEMBERSHIP_STRING = "Level {0}: {1}{2} {3} per {4} (for {5})"

    order = models.IntegerField(blank=False)
    name = models.CharField(max_length=128, blank=False)
    group = models.ForeignKey(LevelGroup, on_delete=models.CASCADE)
    goal = models.IntegerField(blank=False)
    goal_is_percent = models.BooleanField(default=True)
    unit = models.CharField(max_length=32, choices=Unit, blank=False)
    unit_duration = models.CharField(max_length=16, choices=Duration, blank=False)
    total_duration = models.CharField(max_length=16, choices=Duration, blank=False)
    next_level = models.ForeignKey('self', null=True, blank=True, default=None,
                                   on_delete=models.SET_NULL)

    subgoal_1 = models.IntegerField(blank=False)
    subgoal_2 = models.IntegerField(blank=False)
    subgoal_3 = models.IntegerField(blank=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        percent = ""
        if self.goal_is_percent:  percent = "%"
        return Level.MEMBERSHIP_STRING.format(
            self.order,
            self.goal,
            percent,
            self.get_unit_display(),
            self.get_unit_duration_display(),
            self.get_total_duration_display()
        )

    def get_target_strings(self):
        # type: () -> dict
        return {
            strings.KEY_GOAL: '{:,}'.format(self.goal),
            strings.KEY_GOAL_UNIT: self.unit,
            strings.KEY_GOAL_DURATION: DURATIONS.get(self.unit_duration),
            strings.KEY_TOTAL_DURATION: DURATIONS.get(self.total_duration)
        }

    @staticmethod
    def get_level_for_group(group, milestone):
        num_challenges = GroupChallenge.objects.filter(group=group).count()
        if num_challenges > 0:
            return Level.get_next_level(group)
        else:
            return Level.get_first_level(milestone)

    @staticmethod
    def get_next_level(group):
        group_challenge = GroupChallenge.objects.filter(group=group).latest()
        level = group_challenge.level
        return level.next_level

    @staticmethod
    def get_first_level(milestone):
        """
        :param milestone: a Milestone object
        :return: the first level of the Group
        """
        level = Level.objects.filter(group=milestone.level_group).first()
        return level


class GroupChallenge(models.Model):
    MEMBERSHIP_STRING = "{0}'s {1} challenge ({2} - {3})"

    # Other options include models.SET_NULL, models.PROTECT depending on how deletions should be handled.
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=False)
    duration = models.CharField(max_length=16, choices=Duration, blank=False)
    start_datetime = models.DateTimeField(blank=False)
    end_datetime = models.DateTimeField(blank=False)
    completed_datetime = models.DateTimeField(blank=True, null=True)
    # CONFIRM CASCADE IS THE APROPIATE CHANGE
    level = models.ForeignKey(Level, on_delete=models.CASCADE, blank=False)

    class Meta:
        get_latest_by = "end_datetime"

    def __str__(self):
        return GroupChallenge.MEMBERSHIP_STRING.format(
            self.group.name,
            self.duration,
            self.start_datetime,
            self.end_datetime
        )

    def get_target_strings(self):
        # type: () -> dict
        """
        :return: the target strings for the instance of the GroupChallenge.
        Invariant: All group members has the same goal, unit, and durations
        """
        person = Person.objects.get(group=self.group)
        person_challenge = PersonChallenge.objects \
            .filter(person=person, group_challenge=self) \
            .latest(field_name="end_datatime")
        target_strings = {strings.KEY_GOAL_DURATION: self.duration}
        additional_target_strings = person_challenge.get_target_strings()
        return strings.expand_target_strings(target_strings, additional_target_strings)

    def add_member_challenges(self, data):
        # type: (dict) -> list(PersonChallenge)
        """
        Create PersonChallenges for this GroupChallenges using data
        :param data: Dict of input data from AvailableChallengeSerializer
        :return: List of PersonChallenges that was created
        """
        member_challenges = []
        group = self.group
        members = group.members.all()
        for person in members:
            member_challenges.append(PersonChallenge.create_from_data(person, self, data))
        return member_challenges

    def set_as_completed(self):
        self.completed_datetime = timezone.now()
        self.save()

    @staticmethod
    def is_there_a_running_challenge(this_group):
        """
        :param this_group: Group which to be checked
        :return: True if there is GroupChallenge that ended in the future
        """
        running_challenges = GroupChallenge.objects \
            .filter(group=this_group,
                    end_datetime__gte=timezone.now(),
                    completed_datetime__isnull=True)
        return running_challenges.exists()

    @staticmethod
    def is_there_a_passed_challenge(this_group):
        """
        :param this_group: Group which to be checked
        :return: True if there is GroupChallenge that has ended in the past,
        but completed_datetime is null
        """
        running_challenges = GroupChallenge.objects \
            .filter(group=this_group,
                    end_datetime__lt=timezone.now(),
                    completed_datetime__isnull=True)
        return running_challenges.exists()

    @staticmethod
    def get_running_challenge(this_group):
        # type: (Group) -> GroupChallenge
        """
        :param this_group: Group which a challenge exists
        :return: GroupChallenge that is not yet completed but has begun.
        """
        return GroupChallenge.objects \
            .filter(group=this_group,
                    end_datetime__gte=timezone.now(),
                    completed_datetime__isnull=True) \
            .last()

    @staticmethod
    def get_passed_challenge(this_group):
        # type: (Group) -> GroupChallenge
        """
        :param this_group: Group which a challenge exists
        :return: GroupChallenge that is not yet completed but has passed.
        """
        return GroupChallenge.objects \
            .filter(group=this_group,
                    start_datetime__lt=timezone.now(),
                    completed_datetime__isnull=True)\
            .last()

    @staticmethod
    def create_from_data(group, data, steps_average=None):
        """
        :param group: Group in which the GroupChallenge will be created
        :param data: Dict of input data from AvailableChallengeSerializer
        :param steps_average: Currently not used.
        :return: GroupChallenge that has been saved
        """
        start_datetime = GroupChallenge.__get_start_datetime(data)
        end_datetime = GroupChallenge.__get_end_datetime(start_datetime, data)
        level = Level.objects.get(id=data["level_id"])

        group_challenge = GroupChallenge.objects.create(
            group=group,
            duration=data["total_duration"],
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            level=level
        )

        group_challenge.save()
        group_challenge.add_member_challenges(data)
        return group_challenge

    @staticmethod
    def __get_start_datetime(data):
        # today_local = timezone.localtime()  # type: datetime
        # return GroupChallenge.__get_beginning_of_day(today_local) + DATE_DELTA_1D
        if "start_datetime_utc" in data:
            return data["start_datetime_utc"]
        else:
            return GroupChallenge.get_beginning_of_day_local()
            # return timezone.now()

    @staticmethod
    def __get_end_datetime(start_datetime, data):
        total_duration = data['total_duration']
        if total_duration == "1d":
            return start_datetime + DATE_DELTA_1D - DATE_DELTA_1S
        elif total_duration == "7d":
            return start_datetime + DATE_DELTA_7D - DATE_DELTA_1S

    @staticmethod
    def get_beginning_of_day_local():
        # type: () -> datetime
        today_local = timezone.localtime()  # type: datetime
        beginning_datetime_local = today_local.replace(
            hour=0, minute=0, second=0, microsecond=0)  # type: datetime
        beginning_datetime_utc = beginning_datetime_local.astimezone(pytz.utc)
        return beginning_datetime_utc

    ###########################################################################

    @staticmethod
    def create_individualized(group, data):
        # type: (Group, dict) -> GroupChallenge
        """
        :param group: Group in which the GroupChallenge will be created
        :param data: Dict of input data from AvailableChallengeSerializer
        :return: GroupChallenge that has been saved
        """
        start_datetime = GroupChallenge.__get_start_datetime(data)
        end_datetime = GroupChallenge.__get_end_datetime(start_datetime, data)
        level = Level.objects.get(id=data["level_id"])

        group_challenge = GroupChallenge.objects.create(
            group=group,
            duration=data["total_duration"],
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            level=level
        )

        group_challenge.save()
        group_challenge.__add_individualized_challenges(group, data)
        return group_challenge

    def __add_individualized_challenges(self, group, data):
        # type: (Group, dict) -> None
        group_members = dict()  # type: dict()
        group_member_ids = set()  # type: set(str)
        for person in group.members.all():
            group_members[str(person.id)] = person
            group_member_ids.add(str(person.id))

        print(group_members)
        print(group_member_ids)

        picked_challenges = data["challenges_by_person"]  # type: dict

        for key in picked_challenges.keys():
            if key in group_member_ids:
                person = group_members[key]
                person_data = picked_challenges[key]
                PersonChallenge.create_from_data(person, self, person_data)





class PersonChallenge(models.Model):
    MEMBERSHIP_STRING = "{0}'s {1} challenge, {2} {3} per {4} ({5} - {6})"

    person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=False)
    group_challenge = models.ForeignKey(GroupChallenge, on_delete=models.CASCADE, blank=False)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, blank=False)

    unit = models.CharField(max_length=32, choices=Unit, blank=False)
    unit_goal = models.IntegerField(blank=False)
    unit_duration = models.CharField(max_length=16, choices=Duration, blank=False)

    def __str__(self):
        return PersonChallenge.MEMBERSHIP_STRING.format(
            self.person.name,
            self.group_challenge.duration,
            self.unit_goal,
            self.unit,
            self.get_unit_duration_display(),
            self.group_challenge.start_datetime,
            self.group_challenge.end_datetime
        )

    def get_target_strings(self):
        return {
            strings.KEY_GOAL: '{:,}'.format(self.goal),
            strings.KEY_GOAL_UNIT: self.unit,
            strings.KEY_GOAL_DURATION: DURATIONS.get(self.unit_duration)
        }

    @staticmethod
    def create_from_data(person, group_challenge, data):
        """
        :param person: Person that will be associated with the PersonChallenge
        :param group_challenge: Group that will be associated with the PersonChallenge
        :param data: Dict of input data from AvailableChallengeSerializer
        :return: PersonChallenge that from the input parameters
        """
        person_challenge = PersonChallenge.objects.create(
            person=person,
            group_challenge=group_challenge,
            level=group_challenge.level,
            unit=data["unit"],
            unit_goal=data["goal"],
            unit_duration=data["unit_duration"]
        )
        person_challenge.save()
        return person_challenge


class PersonFitnessMilestone(models.Model):
    MEMBERSHIP_STRING = "{0}'s milestone ({1} to {2})"

    person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=False)
    start_datetime = models.DateTimeField(blank=False)
    end_datetime = models.DateTimeField(blank=False)
    steps = models.IntegerField()
    calories = models.FloatField()
    active_minutes = models.IntegerField()
    active_minutes_moderate = models.IntegerField()
    active_minutes_vigorous = models.IntegerField()
    distance = models.FloatField()
    level_group = models.ForeignKey(LevelGroup, on_delete=models.CASCADE, blank=False, default=1)

    class Meta:
        get_latest_by = "end_datetime"

    def __str__(self):
        return PersonFitnessMilestone.MEMBERSHIP_STRING.format(
            self.person.name,
            str(self.start_datetime),
            str(self.end_datetime)
        )

    def get_by_unit(self, unit):
        """
        Get the milestone value of a particular Unit
        :param unit: Unit of interest
        :return: Float or Integer value of the Unit of Interest
        """
        if unit == UNIT_STEPS:
            return self.steps
        elif unit == UNIT_MINUTES:
            return self.active_minutes
        elif unit == UNIT_MINUTES_MODERATE:
            return self.active_minutes_moderate
        elif unit == UNIT_MINUTES_VIGOROUS:
            return self.active_minutes_vigorous
        elif unit == UNIT_DISTANCE:
            return self.distance

    @staticmethod
    def get_latest_from_person():
        # type: (Person) -> PersonFitnessMilestone
        """
        :param person: Person of interest
        :return: The latest PersonFitnessMilestone instance of the said Person
        """
        return PersonFitnessMilestone.objects.latest()

    @staticmethod
    def create_from_7d_average(person, start_date_timezoned, level_group):
        # type: (Person, date, LevelGroup) -> PersonFitnessMilestone
        start_date = start_date_timezoned
        end_date = start_date + DATE_DELTA_7D
        parent_activities = ActivityByDay.objects \
            .filter(person=person,
                    date__gte=start_date,
                    date__lt=end_date) \
            .aggregate(steps=Avg("steps"),
                       calories=Avg("calories"),
                       active_minutes=Avg("active_minutes"),
                       distance=Avg("distance"))

        steps = PersonFitnessMilestone.__get_value(
            parent_activities["steps"], constants.MIN_STEPS, constants.DEFAULT_STEPS)
        cals = PersonFitnessMilestone.__get_value(
            parent_activities["calories"], constants.MIN_CALORIES, constants.DEFAULT_CALORIES)
        mins = PersonFitnessMilestone.__get_value(
            parent_activities["active_minutes"], constants.MIN_ACTIVE_MINUTES, constants.DEFAULT_ACTIVE_MINUTES)
        dist = PersonFitnessMilestone.__get_value(
            parent_activities["distance"], constants.MIN_DISTANCE, constants.DEFAULT_DISTANCE)

        milestone = PersonFitnessMilestone.objects.create(
            person=person,
            start_datetime=start_date,
            end_datetime=end_date,
            steps=steps,
            calories=cals,
            active_minutes=mins,
            active_minutes_moderate=0,
            active_minutes_vigorous=0,
            distance=dist,
            level_group=level_group
        )
        milestone.save()

        return milestone

    @staticmethod
    def __get_value(val, min, default):
        # type: (float) -> float
        if val is None or val < min:
            return default
        else:
            return val

    @staticmethod
    def create_from_predefined_average(person, start_date_timezoned, level_group, steps_average):
        # type: (Person, date, LevelGroup, int) -> PersonFitnessMilestone
        milestone = PersonFitnessMilestone.objects.create(
            person=person,
            start_datetime=start_date_timezoned,
            end_datetime=start_date_timezoned + DATE_DELTA_7D,
            steps=steps_average,
            calories=constants.DEFAULT_CALORIES,
            active_minutes=constants.DEFAULT_ACTIVE_MINUTES,
            active_minutes_moderate=0,
            active_minutes_vigorous=0,
            distance=constants.DEFAULT_DISTANCE,
            level_group=level_group
        )
        milestone.save()

        return milestone
