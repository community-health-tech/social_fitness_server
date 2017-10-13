# STRING CONSTANTS
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
def get_text(unitOfChallenge, textKey, targetStrings):
    """
    Get the text key String based on a unit of challenge
    :param unitOfChallenge: unit of the challenge as defined in models.Unit
    :param textKey: the type of text that is needed
    :param targetStrings: a dictionary of key and target text
    :return: the text with the key string replaces with target string
    """
    output = str(STRINGS_EN_US[unitOfChallenge][textKey])
    for key in targetStrings:
        target = targetStrings[key]
        output = output.replace(key, target)

    return output


def get_target_strings(level, dyad):
    target_strings = {}
    dyad_target_strings = dyad.get_target_strings()
    level_target_strings = level.get_target_strings()

    target_strings.update(dyad_target_strings)
    target_strings.update(level_target_strings)

    return target_strings


def expand_target_strings(targetStrings, additionalStrings):
    """
    Add additionalStrings to targetStrings
    :param targetStrings:
    :param additionalStrings:
    :return: An expanded targetStrings
    """
    for key in additionalStrings:
        targetStrings[key] = additionalStrings[key]

    return targetStrings
