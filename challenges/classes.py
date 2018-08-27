import logging

# from typing import List, Optional

from datetime import datetime
from django.utils import timezone

from fitness.models import PersonFitness, GroupFitness, ActivityByDay, GroupFitnessFactory, DATE_DELTA_7D
from people.models import Group, Person
from challenges import strings
from challenges.abstracts import AbstractChallengeGroup
from challenges.groups import OnePersonGroup, FamilyDyadGroup
from challenges.models import LevelGroup, PersonFitnessMilestone, Level, GroupChallenge, PersonChallenge

logger = logging.getLogger(__name__)


class ChallengeViewModel:
    """Encapsulates data for client's ChallengeManager"""
    STATUS_AVAILABLE = "AVAILABLE"
    STATUS_RUNNING = "RUNNING"
    STATUS_PASSED = "PASSED"

    def __init__(self, group):
        # type: (Group) -> None
        self.status = ChallengeViewModel.__get_challenge_status(group)
        self.available = ChallengeViewModel.__get_available_challenges(group, self.status)
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
    def __get_available_challenges(group, status):
        # type: (Group) -> Optional[ListOfAvailableChallenges]
        if status == ChallengeViewModel.STATUS_AVAILABLE:
            return ListOfAvailableChallenges(group)
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

    def __init__(self, group):
        # type: (Group) -> None
        now = timezone.now()  # type: datetime
        milestone_start_date = now.date() - DATE_DELTA_7D  # type: date
        level_group = LevelGroup.objects.get(pk=1)  # TODO update

        challenge_group = None  # type: AbstractChallengeGroup
        if FamilyDyadGroup.is_type_of(group):
            challenge_group = FamilyDyadGroup(group)
        elif OnePersonGroup.is_type_of(group):
            challenge_group = OnePersonGroup(group)

        reference_person = challenge_group.get_reference_person()
        milestone = PersonFitnessMilestone.create_from_7d_average(reference_person, milestone_start_date, level_group)
        level = Level.get_level_for_group(group, milestone)
        goal = None

        self.is_currently_running = False
        self.text = challenge_group.get_challenge_main_text(level, goal, True)
        self.subtext = challenge_group.get_challenge_secondary_text(level, goal, True)
        self.challenges = ListOfAvailableChallenges.make_list_of_challenges(level, milestone)
        self.total_duration = level.total_duration
        self.start_datetime = now.date()
        self.end_datetime = self.start_datetime + DATE_DELTA_7D
        self.level_id = level.pk
        self.level_order = level.order

    @staticmethod
    def make_list_of_challenges(level, milestone):
        # type: (Level, PersonFitnessMilestone) -> list[AvailableChallenge]
        challenges = [
            AvailableChallenge(1, level, level.subgoal_1, milestone),
            AvailableChallenge(2, level, level.subgoal_2, milestone),
            AvailableChallenge(3, level, level.subgoal_3, milestone)
        ]
        return challenges


class AvailableChallenge:
    """Encapsulates a single available challenge"""

    def __init__(self, order, level, goal, milestone):
        # type: (int, Level, int, PersonFitnessMilestone) -> None
        self.option = order
        self.goal = self.__get_concrete_goal(level, goal, milestone)
        self.unit = level.unit
        self.unit_duration = level.unit_duration
        self.total_duration = level.total_duration
        self.text = strings.get_text_from_dict(level.unit, strings.PICK_DESC, self.__get_target_strings(level, goal))
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




