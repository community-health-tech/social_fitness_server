# Constants
from challenges import strings
from challenges.abstracts import AbstractChallengeGroup
from challenges.models import DURATIONS, Unit, Level
from people.models import Person, Membership, Group, ROLE_PARENT, ROLE_CHILD

""" Classes """


class OnePersonGroup(AbstractChallengeGroup):

    STRINGS_EN_US = {
        "steps": {
            strings.PICK_TEXT: "Pick a steps adventure",
            strings.PICK_SUBTEXT: "%PERSON1_NAME%, you need to do one of these adventures within %TOTAL_DURATION%.",
            strings.PICK_DESC: "Walk around %GOAL% steps every %GOAL_DURATION%!",

            strings.CONFIRM_TEXT: "Walk around %GOAL% steps every %GOAL_DURATION%",
            strings.CONFIRM_SUBTEXT: "As an example, walking around the Boston Common is 2000 steps.",

            strings.INFO_TEXT: "This is your current Steps Adventure",
            strings.INFO_SUBTEXT: "%PERSON1_NAME%, you need to walk %GOAL% steps every %GOAL_DURATION% "
                                  "for %TOTAL_DURATION%.",

            strings.PROGRESS_TEXT: "You are on your way to win your Adventure",
            strings.PROGRESS_SUBTEXT: "You are making good steps so far!",

            strings.COMPLETE_TEXT: "You won the steps challenge",
            strings.COMPLETE_SUBTEXT: "Great job %PERSON1_NAME%!",
        }
    }

    def __init__(self, group):
        if len(group.members.all()) != 1:
            raise ValueError('OnePersonGroup requires Group to have only one member (found %d).' % len(group.members))
        self.person = Person.objects.get(group=group)
        self.membership = self.person.membership_set.get(group=group)
        self.target_strings = None

    @staticmethod
    def is_type_of(group):
        # type: (Group) -> boolean
        return len(group.members.all()) == 1

    def get_reference_person(self):
        # type: () -> models.Person
        return self.person

    def get_target_strings(self):
        # type: () -> dict
        if self.target_strings is None:
            self.target_strings = self.__compute_target_strings()
        else:
            self.target_strings = {}
        return self.target_strings

    def get_challenge_main_text(self, level, goal, is_unstarted_challenge):
        # type: (Level, int, bool) -> str
        keyword_dict = _get_string_dict(level, self, goal=goal)
        return _get_main_text(level.unit, is_unstarted_challenge, OnePersonGroup.STRINGS_EN_US, keyword_dict)

    def get_challenge_secondary_text(self, level, goal, is_unstarted_challenge):
        # type: (Level, int, bool) -> str
        keyword_dict = _get_string_dict(level, self, goal=goal)
        return _get_secondary_text(level.unit, is_unstarted_challenge, OnePersonGroup.STRINGS_EN_US, keyword_dict)

    # PRIVATE CLASS METHODS
    def __compute_target_strings(self):
        return {
            strings.KEY_PERSON1_NAME: self.person.name,
            strings.KEY_PERSON1_PERSONAL: self.membership.pronoun.personal,
            strings.KEY_PERSON1_PRONOUN: self.membership.pronoun.pronoun
        }


class FamilyDyadGroup(AbstractChallengeGroup):

    STRINGS_EN_US = {
        "steps": {
            strings.PICK_TEXT: "Pick a steps adventure",
            strings.PICK_SUBTEXT: "%PERSON1_NAME%, you and %PERSON2_PERSONAL% need to do one of these adventures within %TOTAL_DURATION%.",
            strings.PICK_DESC: "Walk around %GOAL% steps every %GOAL_DURATION%!",

            strings.CONFIRM_TEXT: "Walk around %GOAL% steps every %GOAL_DURATION%",
            strings.CONFIRM_SUBTEXT: "As an example, walking around the Boston Common is 2000 steps.",

            strings.INFO_TEXT: "This is your current Steps Adventure",
            strings.INFO_SUBTEXT: "%PERSON1_NAME% you and %PERSON2_PERSONAL% need to walk %GOAL% steps every %GOAL_DURATION% for %TOTAL_DURATION%.",

            strings.PROGRESS_TEXT: "You are on your way to win your Adventure",
            strings.PROGRESS_SUBTEXT: "You are making good steps so far!",

            strings.COMPLETE_TEXT: "You won the steps challenge",
            strings.COMPLETE_SUBTEXT: "Great job %PERSON1_NAME% and %PERSON2_NAME%!",
        }
    }

    def __init__(self, group):
        # type: (Group) -> None
        if len(group.members.all()) < 2:
            raise ValueError('FamilyDyadGroup require at least two Group members (found %d).' % len(group.members))

        self.group = group
        self.parent = Person.objects.get(
            group=group,
            membership__role=ROLE_PARENT
        )
        self.child = Person.objects.get(
            group=group,
            membership__role=ROLE_CHILD
        )
        self.parent_membership = self.parent.membership_set.get(group=group)
        self.child_membership = self.child.membership_set.get(group=group)
        self.target_strings = None

    def get_reference_person(self):
        # type: () -> models.Person
        return self.group.members.get(membership__role=ROLE_PARENT)

    def get_target_strings(self):
        # type: () -> dict
        if self.target_strings is None:
            self.target_strings = self.__compute_target_strings()
        return self.target_strings

    def get_challenge_main_text(self, level, goal, is_unstarted_challenge):
        # type: (Level, int, bool) -> str
        keyword_dict = _get_string_dict(level, self, goal=goal)
        return _get_main_text(level.unit, is_unstarted_challenge, FamilyDyadGroup.STRINGS_EN_US, keyword_dict)

    def get_challenge_secondary_text(self, level, goal, is_unstarted_challenge):
        # type: (Level, int, bool) -> str
        keyword_dict = _get_string_dict(level, self, goal=goal)
        return _get_secondary_text(level.unit, is_unstarted_challenge, FamilyDyadGroup.STRINGS_EN_US, keyword_dict)

    @staticmethod
    def is_type_of(group):
        # type: (Group) -> bool
        if len(group.members.all()) < 2:
            return False
        else:
            has_parent = False
            has_child = False
            for membership in Membership.objects.filter(group=group):
                if membership.role == ROLE_PARENT:
                    has_parent = True
                if membership.role == ROLE_CHILD:
                    has_child = True
            return has_parent and has_child

    # PRIVATE CLASS METHODS
    def __compute_target_strings(self):
        return {
            strings.KEY_PERSON1_NAME: self.child.name,
            strings.KEY_PERSON1_PERSONAL: self.child_membership.pronoun.personal,
            strings.KEY_PERSON1_PRONOUN: self.child_membership.pronoun.pronoun,
            strings.KEY_PERSON2_NAME: self.parent.name,
            strings.KEY_PERSON2_PERSONAL: self.parent_membership.pronoun.personal,
            strings.KEY_PERSON2_PRONOUN: self.parent_membership.pronoun.pronoun
        }


""" HELPER FUNCTIONS """


def _get_main_text(unit, is_new, text_dict, target_strings):
    # type: (Unit, bool, dict, dict) -> str
    if is_new:
        return strings.get_text(unit, text_dict, strings.CONFIRM_TEXT, target_strings)
    else:
        return strings.get_text(unit, text_dict, strings.INFO_TEXT, target_strings)


def _get_secondary_text(unit, is_new, text_dict, target_strings):
    # type: (Unit, bool, dict, dict) -> str
    if is_new :
        return strings.get_text(unit, text_dict, strings.CONFIRM_SUBTEXT, target_strings)
    else :
        return strings.get_text(unit, text_dict, strings.INFO_SUBTEXT, target_strings)


def _get_string_dict(level, challenge_group, goal=None):
    # type: (Level, AbstractChallengeGroup, int, bool) -> dict
    target_strings = {}
    group_target_strings = challenge_group.get_target_strings()
    level_target_strings = _get_level_string_dict(level)

    target_strings.update(group_target_strings)
    target_strings.update(level_target_strings)

    if goal is not None:
        target_strings[strings.KEY_GOAL] = '{:,}'.format(goal)

    return target_strings


def _get_level_string_dict(level):
    # type: (Level) -> dict
    return {
        strings.KEY_GOAL: '{:,}'.format(level.goal),
        strings.KEY_GOAL_UNIT: level.unit,
        strings.KEY_GOAL_DURATION: DURATIONS.get(level.unit_duration),
        strings.KEY_TOTAL_DURATION: DURATIONS.get(level.total_duration)
    }