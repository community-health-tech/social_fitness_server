import logging

# from typing import List, Optional

from datetime import datetime, date
from django.utils import timezone

from fitness.models import PersonFitness, GroupFitness, ActivityByDay, GroupFitnessFactory, DATE_DELTA_7D
from people.models import Group, Person
from challenges import strings, constants
from challenges.abstracts import AbstractChallengeGroup
from challenges.groups import OnePersonGroup, FamilyDyadGroup
from challenges.models import LevelGroup, PersonFitnessMilestone, Level, GroupChallenge, PersonChallenge

logger = logging.getLogger(__name__)


class ChallengeViewModel:
    """Encapsulates data for client's ChallengeManager"""
    STATUS_AVAILABLE = "AVAILABLE"
    STATUS_RUNNING = "RUNNING"
    STATUS_PASSED = "PASSED"

    def __init__(self, group, steps_average=None):
        # type: (Group, int) -> None
        self.status = ChallengeViewModel.__get_challenge_status(group)
        self.available = ChallengeViewModel.__get_available_challenges(group, self.status, steps_average)
        self.running = ChallengeViewModel.__get_running_challenge(group, self.status)
        self.passed = ChallengeViewModel.__get_passed_challenge(group, self.status)

    @staticmethod
    def __get_challenge_status(group):
        # type: (Group) -> str
        if GroupChallenge.is_there_a_passed_challenge(group):
            return ChallengeViewModel.STATUS_PASSED
        elif GroupChallenge.is_there_a_running_challenge(group):
            return ChallengeViewModel.STATUS_RUNNING
        else:
            return ChallengeViewModel.STATUS_AVAILABLE

    @staticmethod
    def __get_available_challenges(group, status, steps_average):
        # type: (Group, str, int) -> Optional[ListOfAvailableChallenges]
        if status == ChallengeViewModel.STATUS_AVAILABLE:
            return ListOfAvailableChallenges(group, steps_average)
        else:
            return None

    @staticmethod
    def __get_running_challenge(group, status):
        # type: (Group) -> Optional[CurrentChallenge]
        if status == ChallengeViewModel.STATUS_RUNNING:
            challenge = GroupChallenge.objects.filter(group=group).latest()
            return CurrentChallenge(challenge)
        else:
            return None

    @staticmethod
    def __get_passed_challenge(group, status):
        # type: (Group) -> Optional[CurrentChallenge]
        if status == ChallengeViewModel.STATUS_PASSED:
            challenge = GroupChallenge.objects.filter(group=group).latest()
            return CurrentChallenge(challenge, is_new=False, is_running=False)
        else:
            return None


class ListOfAvailableChallenges:
    """Encapsulates all available challenges for a particular group"""

    def __init__(self, group, steps_average=None):
        # type: (Group, str) -> None
        now = datetime.now()  # type: datetime
        milestone_start_date = now - DATE_DELTA_7D  # type: datetime
        start_date = milestone_start_date.date()
        level_group = LevelGroup.objects.get(pk=1)  # TODO update

        challenge_group = None  # type: AbstractChallengeGroup
        if FamilyDyadGroup.is_type_of(group):
            challenge_group = FamilyDyadGroup(group)
        elif OnePersonGroup.is_type_of(group):
            challenge_group = OnePersonGroup(group)

        reference_person = challenge_group.get_reference_person()
        milestone = self.__get_milestone(reference_person, start_date, level_group, steps_average)
        level = Level.get_level_for_group(group, milestone)
        goal = int(level.subgoal_2 * milestone.steps / 100)  # type: int

        self.is_currently_running = False
        self.text = challenge_group.get_challenge_main_text(level, goal, True)
        self.subtext = challenge_group.get_challenge_secondary_text(level, goal, True)
        self.start_datetime = now.date()
        self.end_datetime = self.start_datetime + DATE_DELTA_7D
        self.challenges = ListOfAvailableChallenges.__make_list_of_challenges(level, milestone, self.start_datetime)
        self.challenges_by_person = ListOfAvailableChallenges\
            .__make_list_of_challenges_by_person(group, start_date, level_group, steps_average)
        self.total_duration = level.total_duration
        self.level_id = level.pk
        self.level_order = level.order

    @staticmethod
    def __make_list_of_challenges(level, milestone, start_datetime_utc):
        # type: (Level, PersonFitnessMilestone, datetime) -> list[AvailableChallenge]
        challenges = [
            AvailableChallenge(1, level, level.subgoal_1, milestone, start_datetime_utc),
            AvailableChallenge(2, level, level.subgoal_2, milestone, start_datetime_utc),
            AvailableChallenge(3, level, level.subgoal_3, milestone, start_datetime_utc)
        ]
        return challenges

    @staticmethod
    def __get_milestone(person, start_date, level_group, steps_average_str):
        # type: (Person, date, LevelGroup, str) -> PersonFitnessMilestone
        if steps_average_str is None:
            return PersonFitnessMilestone.create_from_7d_average(person, start_date, level_group)
        else:
            steps_average = int(steps_average_str)
            return PersonFitnessMilestone.create_from_predefined_average(person, start_date, level_group, steps_average)

    @staticmethod
    def __make_list_of_challenges_by_person(group, start_date, prior_level_group, steps_average_str):
        # type: (Group, date, LevelGroup, str) -> dict
        list_of_challenges_by_person = dict() # type: dict
        for person in group.members.all():
            milestone = ListOfAvailableChallenges.__get_milestone(person, start_date, prior_level_group, steps_average_str)
            new_level = Level.get_level_for_group(group, milestone)
            challenges = ListOfAvailableChallenges.__make_list_of_challenges(new_level, milestone)
            list_of_challenges_by_person[person.id] = challenges

        return list_of_challenges_by_person


class AvailableChallenge:
    """Encapsulates a single available challenge"""

    def __init__(self, order, level, goal, milestone, start_datetime_utc):
        # type: (int, Level, int, PersonFitnessMilestone, datetime) -> None
        self.option = order
        self.goal = self.__get_concrete_goal(level, goal, milestone)
        self.unit = level.unit
        self.unit_duration = level.unit_duration
        self.total_duration = level.total_duration
        self.start_datetime_utc = start_datetime_utc
        self.text = strings.get_text_from_dict(level.unit, strings.PICK_DESC, self.__get_target_strings(level, self.goal))
        self.level_id = level.pk

    def __get_concrete_goal(self, level, goal, milestone):
        # type: (Level, int, PersonFitnessMilestone) -> int
        concrete_goal = self.__compute_concrete_goal(level, goal, milestone)
        return int(round(concrete_goal, -1))

    @staticmethod
    def __compute_concrete_goal(level, goal, milestone):
        # type: (Level, int, PersonFitnessMilestone) -> int
        if level.goal_is_percent:
            return (goal * milestone.get_by_unit(level.unit)) / 100
        else:
            return goal

    @staticmethod
    def __get_target_strings(level, goal):
        # type: (Level, int) -> dict
        target_strings = level.get_target_strings()
        target_strings[strings.KEY_GOAL] = '{:,}'.format(goal)
        return target_strings


class CurrentChallenge:
    """Encapsulates a currently running GroupChallenge"""

    def __init__(self, group_challenge, is_new=False, is_running=True):
        # type: (GroupChallenge, bool, bool) -> None
        group = group_challenge.group  # type: Group
        challenge_group = None  # type: AbstractChallengeGroup

        if FamilyDyadGroup.is_type_of(group):
            challenge_group = FamilyDyadGroup(group)
        elif OnePersonGroup.is_type_of(group):
            challenge_group = OnePersonGroup(group)

        reference_person = challenge_group.get_reference_person()  # type: Person
        level = group_challenge.level  # type: Level
        reference_person_challenge = PersonChallenge.objects\
            .filter(group_challenge=group_challenge, person=reference_person)\
            .get()  # type: PersonChallenge
        goal = reference_person_challenge.unit_goal

        self.is_currently_running = is_running  # type: bool
        self.text = challenge_group.get_challenge_main_text(level, goal, is_new)  # type: str
        self.subtext = challenge_group.get_challenge_secondary_text(level, goal, is_new)  # type: str
        self.total_duration = group_challenge.duration  # type: int
        self.start_datetime = group_challenge.start_datetime  # type: datetime
        self.end_datetime = group_challenge.end_datetime  # type: datetime
        self.level_id = group_challenge.level.id  # type: int
        self.level_order = group_challenge.level.order  # type: int
        self.challenges = group_challenge.personchallenge_set.all()
        self.progress = CurrentChallenge.__get_progress(  # type: List[PersonProgress]
            GroupFitnessFactory.get(group.id, self.start_datetime.date(), self.end_datetime.date()),
            self.challenges)

    @staticmethod
    def __get_progress(group_fitness, person_challenge_set):
        # type: (GroupFitness, List[PersonChallenge]) -> List[PersonProgress]
        group_fitness_progress = []  # type: List[PersonProgress]
        for person_fitness in group_fitness.activities:
            person_challenge = CurrentChallenge.__get_person_challenge_from_set(person_fitness.id,
                                                                                person_challenge_set)
            group_fitness_progress.append(PersonProgress(person_fitness, person_challenge))
        return group_fitness_progress

    @staticmethod
    def __get_person_challenge_from_set(person_id, person_challenge_set):
        # type: (int, list[PersonChallenge]) -> PersonChallenge
        person_challenge_filtered = list(filter(lambda person_challenge: person_challenge.person.id == person_id,
                                                person_challenge_set))
        return person_challenge_filtered[0]


class PersonProgress:
    def __init__(self, person_fitness, person_challenge):
        # type: (PersonFitness, PersonChallenge) -> None
        self.person_id = person_challenge.person.id  # type: int
        self.goal = person_challenge.unit_goal  # type: int
        self.unit = person_challenge.unit  # type: str
        self.unit_duration = person_challenge.unit_duration  # type: str
        self.progress = PersonProgress.__get_person_progress(person_fitness)  # type: List[int]
        self.progress_percent = PersonProgress.__get_progress_percent(self.progress, self.goal)  # type: List[float]
        self.progress_achieved = PersonProgress.__get_is_goal_achieved(self.progress_percent)  # type: List[bool]
        self.total_progress = PersonProgress.__get_total_progress(self.progress)  # type: int

    @staticmethod
    def __get_person_progress(person_fitness):
        # type: (PersonFitness) -> List[int]
        daily_progress = []  # type: List[int]
        for activity_by_day in person_fitness.activities:
            daily_progress.append(activity_by_day.steps)
        return daily_progress

    @staticmethod
    def __get_progress_percent(person_daily_progress, goal):
        # type: (List[int], int) -> List[float]
        return list(map(lambda one_day_progress: PersonProgress.__get_percent(one_day_progress, goal),
                        person_daily_progress))

    @staticmethod
    def __get_is_goal_achieved(person_daily_progress_percent):
        # type: (List(float)) -> List[bool]
        return list(map(lambda progress_percent: PersonProgress.__get_progress_achieved(progress_percent),
                        person_daily_progress_percent))

    @staticmethod
    def __get_total_progress(person_daily_progress):
        # type: (List(int)) -> int
        total_progress = 0  # type: int
        for one_day_steps in person_daily_progress:
            total_progress += one_day_steps
        return total_progress

    @staticmethod
    def __get_percent(one_day_progress, goal):
        # type: (int, int) -> Optional[float]
        if goal >= 1:
            return round(100.0 * one_day_progress / goal, 3)
        else:
            return None

    @staticmethod
    def __get_progress_achieved(one_day_progress_percent):
        # type: (float) -> Optional[bool]
        if one_day_progress_percent is not None:
            return True if one_day_progress_percent >= 100.0 else False
        else:
            return None




