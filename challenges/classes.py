from challenges import strings
from challenges.models import LevelGroup, PersonFitnessMilestone, Level, \
    GroupChallenge, PersonChallenge
from challenges.models import UNIT_STEPS
from people.family import FamilyDyad
from people.models import ROLE_PARENT


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

        if FamilyDyad.is_family(group):
            """
            dyad = FamilyDyad(group)
            caregiver = group.members.get(membership__role=ROLE_PARENT)
            milestone = PersonFitnessMilestone.create_from_7d_average(
                caregiver, ROLE_PARENT, __TEMP_DATE, __TEMP_LEVEL_GROUP)
            level = Level.get_level_for_group(group, milestone)
            str_dict = strings.get_string_dict(level, dyad)

            self.is_currently_running = False
            self.text = strings.get_text(UNIT_STEPS, strings.PICK_TEXT, str_dict)
            self.subtext = strings.get_text(UNIT_STEPS, strings.PICK_SUBTEXT, str_dict)
            self.challenges = self.make_list_of_challenges(level, milestone, str_dict)
            self.total_duration = level.total_duration
            self.start_datetime = None #timezone.now()
            self.end_datetime = None #self.start_datetime + DATE_DELTA_7D
            self.level_id = level.pk
            self.level_order = level.order"""
            pass
        else: ## TODO: make this better, this is a hack by HS
            person = group.members.get()
            milestone = PersonFitnessMilestone.create_from_7d_average(
                person, ROLE_PARENT, __TEMP_DATE, __TEMP_LEVEL_GROUP) # TODO role is not needed
            level = Level.get_level_for_group(group, milestone)
            str_dict = {}
            self.is_currently_running = False
            self.text = strings.get_text(UNIT_STEPS, strings.PICK_TEXT, str_dict)
            self.subtext = strings.get_text(UNIT_STEPS, strings.PICK_SUBTEXT, str_dict)
            self.challenges = self.make_list_of_challenges(level, milestone, str_dict)
            self.total_duration = level.total_duration
            self.start_datetime = None #timezone.now()
            self.end_datetime = None #self.start_datetime + DATE_DELTA_7D
            self.level_id = level.pk
            self.level_order = level.order


    def make_list_of_challenges(self, level, milestone, target_strings):
        challenges = [
            AvailableChallenge(1, level, level.subgoal_1, milestone, target_strings),
            AvailableChallenge(2, level, level.subgoal_2, milestone, target_strings),
            AvailableChallenge(3, level, level.subgoal_3, milestone, target_strings)
        ]
        return challenges


class AvailableChallenge():
    """Encapsulates a single available challenge"""

    def __init__(self, order, level, goal, milestone, target_strings):
        self.option = order
        self.goal = self.__get_concrete_goal(level, goal, milestone)
        target_strings = self.__get_target_strings(target_strings, self.goal)
        self.unit = level.unit
        self.unit_duration = level.unit_duration
        self.total_duration = level.total_duration
        self.text = strings.get_text(level.unit, strings.PICK_DESC, target_strings)
        self.level_id = level.pk

    def __get_concrete_goal(self, level, goal, milestone):
        concrete_goal = self.__compute_concrete_goal(level, goal, milestone)
        return int(round(concrete_goal, -1))

    def __compute_concrete_goal(self, level, goal, milestone):
        if level.goal_is_percent :
            return (goal * milestone.get_by_unit(level.unit)) / 100
        else :
            return goal

    def __get_target_strings(self, target_strings, goal):
        target_strings[strings.KEY_GOAL] = '{:,}'.format(goal)
        return target_strings


class CurrentChallenge():
    """Encapsulates a currently running GroupChallenge"""

    def __init__(self, group_challenge, is_new=False):
        """
        :type group_challenge: GroupChallenge
        """
        level = group_challenge.level
        group = group_challenge.group
        dyad = FamilyDyad(group)
        caregiver = group.members.get(membership__role=ROLE_PARENT)
        caregiver_challenge = PersonChallenge.objects\
            .filter(group_challenge=group_challenge, person=caregiver)\
            .get()
        goal = caregiver_challenge.unit_goal
        str_dict = strings.get_string_dict(level, dyad, goal=goal)

        self.is_currently_running = True
        self.text = self.__get_text(level.unit, is_new, str_dict)
        self.subtext = self.__get_subtext(level.unit, is_new, str_dict)
        self.total_duration = group_challenge.duration
        self.start_datetime = group_challenge.start_datetime
        self.end_datetime = group_challenge.end_datetime
        self.level_id = group_challenge.level.id
        self.level_order = group_challenge.level.order
        self.progress = group_challenge.personchallenge_set.all()

    def __get_text(self, unit, is_new, target_strings):
        if is_new :
            return strings.get_text(unit, strings.CONFIRM_TEXT, target_strings)
        else :
            return strings.get_text(unit, strings.INFO_TEXT, target_strings)

    def __get_subtext(self, unit, is_new, target_strings):
        if is_new :
            return strings.get_text(unit, strings.CONFIRM_SUBTEXT, target_strings)
        else :
            return strings.get_text(unit, strings.INFO_SUBTEXT, target_strings)


