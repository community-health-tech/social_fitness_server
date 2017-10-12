from challenges import strings
from challenges.models import LevelGroup, PersonFitnessMilestone, Level
from challenges.models import UNIT_STEPS
from people.family import FamilyDyad
from people.models import ROLE_PARENT


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
    """Encapsulates a single challenge"""

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