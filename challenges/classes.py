from challenges import strings
from challenges.models import LevelGroup, PersonFitnessMilestone, Level, \
    GroupChallenge
from challenges.models import UNIT_STEPS
from people.family import FamilyDyad
from people.models import ROLE_PARENT


class ListOfAvailableChallenges():
    """Encapsulates all available challenges for a particular group"""

    def __init__(self, group):#, group, level, milestone):
        __TEMP_DATE = "2017-06-01"
        __TEMP_LEVEL_GROUP = LevelGroup.objects.get(pk=1)

        dyad = FamilyDyad(group)
        caregiver = group.members.get(membership__role=ROLE_PARENT)
        milestone = PersonFitnessMilestone.create_from_7d_average(
            caregiver, ROLE_PARENT, __TEMP_DATE, __TEMP_LEVEL_GROUP)
        level = Level.get_level_for_group(group, milestone)
        str_dict = strings.get_string_dict(level, dyad)

        self.text = strings.get_text(UNIT_STEPS, strings.PICK_TEXT, str_dict)
        self.subtext = strings.get_text(UNIT_STEPS, strings.PICK_SUBTEXT, str_dict)
        self.challenges = self.make_list_of_challenges(level, milestone, str_dict)
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
        target_strings = self.__get_target_strings(target_strings)
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

    def __get_target_strings(self, target_strings):
        target_strings[strings.KEY_GOAL] = str(self.goal)
        return target_strings


class CurrentChallenge():
    """Encapsulates a currently running GroupChallenge"""

    def __init__(self, group_challenge, is_new=False):
        """
        :type group_challenge: GroupChallenge
        """
        dyad = FamilyDyad(group_challenge.group)
        level = group_challenge.level
        str_dict = strings.get_string_dict(level, dyad)

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


