# STRING CONSTANTS
import re
import sys

KEY_GOAL = "%GOAL%"
KEY_GOAL_UNIT = "%KEY_GOAL_UNIT%"
KEY_GOAL_DURATION = "%GOAL_DURATION%"
KEY_TOTAL_DURATION = "%TOTAL_DURATION%"

PICK_TEXT = "PICK_TEXT"
PICK_SUBTEXT = "PICK_SUBTEXT"
PICK_DESC = "PICK_DESC"
CONFIRM_TEXT = "CONFIRM_TEXT"
CONFIRM_SUBTEXT = "CONFIRM_SUBTEXT"
INFO_TEXT = "INFO_TEXT"
INFO_SUBTEXT = "INFO_SUBTEXT"
PROGRESS_TEXT = "PROGRESS_TEXT"
PROGRESS_SUBTEXT = "PROGRESS_SUBTEXT"
COMPLETE_TEXT = "COMPLETE_TEXT"
COMPLETE_SUBTEXT = "COMPLETE_SUBTEXT"

STRINGS_EN_US = {
    "steps": {
        PICK_TEXT: "Pick a steps adventure",
        PICK_SUBTEXT: "%PERSON1_NAME%, you and %PERSON2_PERSONAL% need to do one of these adventures within %TOTAL_DURATION%.",
        PICK_DESC: "Walk around %GOAL% steps every %GOAL_DURATION%!",

        CONFIRM_TEXT: "Walk around %GOAL% steps every %GOAL_DURATION%",
        CONFIRM_SUBTEXT: "As an example, walking around the Boston Common is 2000 steps.",

        INFO_TEXT: "This is your current Steps Adventure",
        INFO_SUBTEXT: "%PERSON1_NAME% you and %PERSON2_PERSONAL% need to walk %GOAL% steps every %GOAL_DURATION% for %TOTAL_DURATION%.",

        PROGRESS_TEXT: "You are on your way to win your Adventure",
        PROGRESS_SUBTEXT: "You are making good steps so far!",

        COMPLETE_TEXT: "You won the steps challenge",
        COMPLETE_SUBTEXT: "Great job %PERSON1_NAME% and %PERSON2_NAME%!",
    }
}

# FUNCTIONS
def get_text(unit, text_key, str_dict):
    """
    Get the text key String based on a unit of challenge
    :param unit: unit of the challenge as defined in models.Unit
    :param textKey: String of the type of text that is needed
    :param targetStrings: Dict of key and target texts
    :return: String with the key string replaces with target string
    """
    text = str(STRINGS_EN_US[unit][text_key])
    return __get_text_using_regex(text, str_dict)


def get_string_dict(level, dyad, goal=None):
    """
    Given a Level
    :param level:
    :param dyad:
    :return:
    """
    target_strings = {}
    dyad_target_strings = dyad.get_target_strings()
    level_target_strings = level.get_target_strings()

    target_strings.update(dyad_target_strings)
    target_strings.update(level_target_strings)

    if goal != None :
        target_strings[KEY_GOAL] = '{:,}'.format(goal)

    return target_strings


def expand_string_dict(targetStrings, additionalStrings):
    """
    Add additionalStrings to targetStrings
    :param targetStrings:
    :param additionalStrings:
    :return: An expanded targetStrings
    """
    for key in additionalStrings: targetStrings[key] = additionalStrings[key]
    return targetStrings

# HELPER FUNCTIONS
def __get_text_using_replace (string, str_dict):
    """
    Given a string, replace the occurrence of keys in str_dict with the values
    :param string:
    :param str_dict:
    :return: Str
    """
    for key in str_dict:
        target = str_dict[key]
        string = string.replace(key, target)
    return string

def __get_text_using_regex(text, str_dict):
    """
    Given a string, replace the occurrence of keys in str_dict with the values.
    This is the more efficient approach for replacement by using Regex.
    :param string:
    :param str_dict:
    :return: Str
    """
    pattern, rep = __get_replacement_pattern(str_dict)
    return pattern.sub(lambda m: rep[re.escape(m.group(0))], text)

def __get_replacement_pattern(str_dict):
    """
    :param str_dict: Dict of key and target_text pairs
    :return: RegularExpression object
    """
    if sys.version_info[0] < 3:
        iters = str_dict.iteritems()
    else:
        iters = str_dict.items()

    rep = dict((re.escape(k), v) for k, v in iters)
    pattern = re.compile("|".join(str_dict.keys()))

    return pattern, rep
