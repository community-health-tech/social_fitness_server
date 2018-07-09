import logging

from challenges import strings, groups
from challenges.models import LevelGroup, PersonFitnessMilestone, Level, \
    GroupChallenge, PersonChallenge

logger = logging.getLogger(__name__)


class ChallengeViewModel():
    """Encapsulates data for client's ChallengeManager"""
    STATUS_AVAILABLE = "AVAILABLE"
    STATUS_RUNNING = "RUNNING"

    def __init__(self, group):
        self.status = ChallengeViewModel.__get_challenge_status(group)
        self.available = ChallengeViewModel.__get_available_challenges(group, self.status)
        self.running = ChallengeViewModel.__get_running_challenges(group, self.status)

    @staticmethod
    def __get_challenge_status(group):
        if GroupChallenge.is_there_a_running_challenge(group) :
            return ChallengeViewModel.STATUS_RUNNING
        else:
            return ChallengeViewModel.STATUS_AVAILABLE

    @staticmethod
    def __get_available_challenges(group, status):
        if status == ChallengeViewModel.STATUS_AVAILABLE:
            return ListOfAvailableChallenges(group)
        else:
            return None

    @staticmethod
    def __get_running_challenges(group, status):
        if status == ChallengeViewModel.STATUS_RUNNING:
            challenge = GroupChallenge.objects.filter(group=group).latest()
            return CurrentChallenge(challenge)
        else:
            return None


class ListOfAvailableChallenges():
    """Encapsulates all available challenges for a particular group"""

    def __init__(self, group):#, group, level, milestone):
        __TEMP_DATE = "2017-06-01"
        __TEMP_LEVEL_GROUP = LevelGroup.objects.get(pk=1)

        if groups.FamilyDyadGroup.is_type_of(group):
            challenge_group = groups.FamilyDyadGroup(group)
        elif groups.OnePersonGroup.is_type_of(group):
            challenge_group = groups.OnePersonGroup(group)

        reference_person = challenge_group.get_reference_person()
        milestone = PersonFitnessMilestone.create_from_7d_average(reference_person, __TEMP_DATE, __TEMP_LEVEL_GROUP)
        level = Level.get_level_for_group(group, milestone)
        goal = None

        self.is_currently_running = False
        self.text = challenge_group.get_challenge_main_text(level, goal, True)
        self.subtext = challenge_group.get_challenge_secondary_text(level, goal, True)
        self.challenges = ListOfAvailableChallenges.make_list_of_challenges(level, milestone)
        self.total_duration = level.total_duration
        self.start_datetime = None #timezone.now() TODO
        self.end_datetime = None #self.start_datetime + DATE_DELTA_7D
        self.level_id = level.pk
        self.level_order = level.order

    @staticmethod
    def make_list_of_challenges(level, milestone):
        challenges = [
            AvailableChallenge(1, level, level.subgoal_1, milestone),
            AvailableChallenge(2, level, level.subgoal_2, milestone),
            AvailableChallenge(3, level, level.subgoal_3, milestone)
        ]
        return challenges


class AvailableChallenge():
    """Encapsulates a single available challenge"""

    def __init__(self, order, level, goal, milestone):
        self.option = order
        self.goal = self.__get_concrete_goal(level, goal, milestone)
        self.unit = level.unit
        self.unit_duration = level.unit_duration
        self.total_duration = level.total_duration
        self.text = strings.get_text(level.unit, strings.PICK_DESC, self.__get_target_strings(level, goal))
        self.level_id = level.pk

    def __get_concrete_goal(self, level, goal, milestone):
        concrete_goal = self.__compute_concrete_goal(level, goal, milestone)
        return int(round(concrete_goal, -1))

    @staticmethod
    def __compute_concrete_goal(level, goal, milestone):
        if level.goal_is_percent:
            return (goal * milestone.get_by_unit(level.unit)) / 100
        else:
            return goal

    @staticmethod
    def __get_target_strings(self, level, goal):
        # type: (Level, int) -> dict
        target_strings = level.get_target_strings()
        target_strings[strings.KEY_GOAL] = '{:,}'.format(goal)
        return target_strings


class CurrentChallenge():
    """Encapsulates a currently running GroupChallenge"""

    def __init__(self, group_challenge, is_new=False):
        """
        :type group_challenge: GroupChallenge
        """
        group = group_challenge.group

        if groups.FamilyDyadGroup.is_type_of(group):
            challenge_group = groups.FamilyDyadGroup(group)
        elif groups.OnePersonGroup.is_type_of(group):
            challenge_group = groups.OnePersonGroup(group)

        reference_person = challenge_group.get_reference_person()
        level = group_challenge.level
        reference_person_challenge = PersonChallenge.objects\
            .filter(group_challenge=group_challenge, person=reference_person)\
            .get()
        goal = reference_person_challenge.unit_goal

        self.is_currently_running = True
        self.text = challenge_group.get_challenge_main_text(level, goal, is_new)
        self.subtext = challenge_group.get_challenge_secondary_text(level, goal, is_new)
        self.total_duration = group_challenge.duration
        self.start_datetime = group_challenge.start_datetime
        self.end_datetime = group_challenge.end_datetime
        self.level_id = group_challenge.level.id
        self.level_order = group_challenge.level.order
        self.progress = group_challenge.personchallenge_set.all()


