from challenges.models import Level
from people import models


class AbstractChallengeGroup():

    @staticmethod
    def is_type_of(self):
        # type: (models.Group) -> boolean
        raise NotImplementedError()

    def get_reference_person(self):
        # type: () -> models.Person
        raise NotImplementedError()

    def get_target_strings(self):
        # type: () -> dict
        raise NotImplementedError()

    def get_challenge_main_text(self, level, goal, is_unstarted_challenge):
        # type: (Level, int, bool) -> str
        raise NotImplementedError()

    def get_challenge_secondary_text(self, level, goal, is_unstarted_challenge):
        # type: (Level, int, bool) -> str
        raise NotImplementedError()