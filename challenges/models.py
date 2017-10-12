from dateutil import parser
from django.db import models
from django.db.models import Avg

from challenges import strings
from people.family import FamilyDyad
from people.models import Person, Group, Membership, ROLE_CHILD, ROLE_PARENT
from fitness.models import ActivityByDay, DATE_DELTA_1D, DATE_DELTA_7D

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
    ('12h', 'half day'),
    ('1d', 'one day'),
    ('2d', 'two day'),
    ('3d', 'three day'),
    ('3d', 'three day'),
    ('7d', 'one week')
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
        if self.goal_is_percent :  percent = "%"
        return Level.MEMBERSHIP_STRING.format(
            self.order,
            self.goal,
            percent,
            self.get_unit_display(),
            self.get_unit_duration_display(),
            self.get_total_duration_display()
        )

    def get_target_strings(self):
        return {
            strings.KEY_GOAL: str(self.goal),
            strings.KEY_GOAL_UNIT: self.unit,
            strings.KEY_GOAL_DURATION: DURATIONS.get(self.unit_duration),
            strings.KEY_TOTAL_DURATION: DURATIONS.get(self.total_duration)
        }

    @staticmethod
    def get_level_for_group(group, milestone):
        level = None
        num_challenges = GroupChallenge.objects.filter(group=group).count()
        if num_challenges > 0:
            level = Level.get_next_level(group, milestone)
        else:
            level = Level.get_first_level(group, milestone)
        return level

    @staticmethod
    def get_next_level(group, milestone):
        group_challenge = GroupChallenge.objects.filter(group=group).latest()
        person_challenge = PersonChallenge.objects\
            .get(group_challenge=group_challenge)
        prev_level = Level.objects.get(level=person_challenge.level)
        next_level = Level.objects.get(level=prev_level)
        return next_level

    @staticmethod
    def get_first_level(group, milestone):
        """
        :param group: a Group object
        :return: the first level of the Group
        """
        level = Level.objects.filter(group=milestone.level_group).first()
        return level


class GroupChallenge(models.Model):
    MEMBERSHIP_STRING = "{0}'s {1} challenge ({2} - {3})"

    group = models.ForeignKey(Group, blank=False)
    duration = models.CharField(max_length=16, choices=Duration, blank=False)
    start_datetime = models.DateTimeField(blank=False)
    end_datetime = models.DateTimeField(blank=False)
    completed_datetime = models.DateTimeField()

    def __str__(self):
        return Level.MEMBERSHIP_STRING.format(
            self.group.name,
            self.duration,
            self.start_datetime,
            self.end_datetime
        )

    class Meta:
        get_latest_by = "end_datetime"

    def get_target_strings(self):
        """
        :return: the target strings for the instance of the GroupChallenge.
        Invariant: All group members has the same goal, unit, and durations
        """
        person = Person.objects.get(group=self.group)
        person_challenge = PersonChallenge.objects\
            .filter(person=person, group_challenge=self)\
            .latest(field_name="end_datatime")
        target_strings = {strings.KEY_GOAL_DURATION: self.duration}
        additional_target_strings = person_challenge.get_target_strings()

        return strings.expand_target_strings(target_strings, additional_target_strings)


class PersonChallenge(models.Model):
    MEMBERSHIP_STRING = "{0}'s {1} challenge, {2} {3} per {4} ({5} - {6})"

    person = models.ForeignKey(Person, blank=False)
    group_challenge = models.ForeignKey(GroupChallenge, blank=False)
    level = models.ForeignKey(Level, blank=False)

    unit =  models.CharField(max_length=32, choices=Unit, blank=False)
    unit_goal = models.IntegerField(blank=False)
    unit_duration = models.CharField(max_length=16, choices=Duration, blank=False)

    def __str__(self):
        return Level.MEMBERSHIP_STRING.format(
            self.person.name,
            self.group_challenge.duration,
            self.unit_goal,
            self.unit,
            self.get_unit_duration_display(),
            self.start_datetime,
            self.end_datetime
        )

    def get_target_strings(self):
        return {
            strings.KEY_GOAL: str(self.unit_goal),
            strings.KEY_GOAL_UNIT: self.unit,
            strings.KEY_GOAL_DURATION: DURATIONS.get(self.unit_duration)
        }


class PersonFitnessMilestone(models.Model):
    MEMBERSHIP_STRING = "{0}'s milestone ({1} to {2})"

    person = models.ForeignKey(Person, blank=False)
    start_datetime = models.DateTimeField(blank=False)
    end_datetime = models.DateTimeField(blank=False)
    steps = models.IntegerField()
    calories = models.FloatField()
    active_minutes = models.IntegerField()
    active_minutes_moderate = models.IntegerField()
    active_minutes_vigorous = models.IntegerField()
    distance = models.FloatField()
    level_group = models.ForeignKey(LevelGroup, blank=False, default=1)

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
        if unit == UNIT_STEPS :
            return self.steps
        elif unit == UNIT_MINUTES :
            return self.active_minutes
        elif unit == UNIT_MINUTES_MODERATE:
            return self.active_minutes_moderate
        elif unit == UNIT_MINUTES_VIGOROUS:
            return self.active_minutes_vigorous
        elif unit == UNIT_DISTANCE:
            return self.distance

    @staticmethod
    def get_latest_from_person(person):
        """
        :param person: Person of interest
        :return: The latest PersonFitnessMilestone instance of the said Person
        """
        return PersonFitnessMilestone.objects.latest()

    @staticmethod
    def create_from_7d_average(person, role, start_date_string, level_group):
        start_date = parser.parse(start_date_string)
        end_date = start_date + DATE_DELTA_7D
        parent_activities = ActivityByDay.objects\
            .filter(
            person = person,
            date__gte = start_date,
            date__lt = end_date)\
            .aggregate(
            steps = Avg("steps"),
            calories = Avg("calories"),
            active_minutes = Avg("active_minutes"),
            distance = Avg("distance")
        )

        milestone = PersonFitnessMilestone.objects.create(
            person=person,
            start_datetime=start_date,
            end_datetime=end_date,
            steps=parent_activities["steps"],
            calories=parent_activities["calories"],
            active_minutes=parent_activities["active_minutes"],
            active_minutes_moderate=0,
            active_minutes_vigorous=0,
            distance=parent_activities["distance"],
            level_group=level_group
        )
        milestone.save()

        return milestone



# Regular models
class AvailableChallenges():
    """Encapsulates all available challenges for a particular group"""

    def __init__(self, group):#, group, level, milestone):
        __TEMP_DATE = "2017-06-01"
        __TEMP_LEVEL_GROUP = LevelGroup.objects.get(pk=1)

        caregiver = group.members.get(membership__role=ROLE_PARENT)
        #milestone = PersonFitnessMilestone.get_latest_from_person(person)
        milestone = PersonFitnessMilestone.create_from_7d_average(
            caregiver, ROLE_PARENT, __TEMP_DATE, __TEMP_LEVEL_GROUP)

        level = Level.get_level_for_group(group, milestone)
        dyad = FamilyDyad(group)
        target_strings = self.__get_target_strings(level, dyad)

        self.text = strings.get_text(UNIT_STEPS, strings.PICK_TEXT, target_strings)
        self.subtext = strings.get_text(UNIT_STEPS, strings.PICK_SUBTEXT, target_strings)
        self.challenges = self.make_list_of_challenges(level, milestone, target_strings)

    def make_list_of_challenges(self, level, milestone, target_strings):
        challenges = [
            Challenge(level, level.subgoal_1, milestone, target_strings),
            Challenge(level, level.subgoal_2, milestone, target_strings),
            Challenge(level, level.subgoal_3, milestone, target_strings)
        ]
        return challenges

    def __get_target_strings(self, level, dyad):
        target_strings = {}
        dyad_target_strings = dyad.get_target_strings()
        level_target_strings = level.get_target_strings()

        target_strings.update(dyad_target_strings)
        target_strings.update(level_target_strings)

        return target_strings


class Challenge():
    """Encapsulates one challenge"""

    def __init__(self, level, goal, milestone, target_strings):
        self.order = level.order
        self.goal = self.__get_concrete_goal(level, goal, milestone)
        self.unit = level.unit
        self.unit_duration = level.unit_duration
        self.total_duration = level.total_duration
        self.text = self.__get_text(level, target_strings)

    def __get_concrete_goal(self, level, goal, milestone):
        concrete_goal = goal
        if level.goal_is_percent :
            concrete_goal =  (goal * milestone.get_by_unit(level.unit)) / 100
        return int(round(concrete_goal, -1))

    def __get_text (self, level, target_strings):
        return strings.get_text(
            level.unit,
            strings.PICK_DESC,
            self.__get_target_strings(target_strings)
        )

    def __get_target_strings(self, target_strings):
        target_strings[strings.KEY_GOAL] = str(self.goal)
        return target_strings



