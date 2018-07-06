# Constants
from people.models import Person, Membership, ROLE_PARENT, ROLE_CHILD

KEY_PERSON1_NAME = "%PERSON1_NAME%"
KEY_PERSON1_PERSONAL = "%PERSON1_PERSONAL%"
KEY_PERSON1_PRONOUN = "%PERSON1_PRONOUN%"
KEY_PERSON2_NAME = "%PERSON2_NAME%"
KEY_PERSON2_PRONOUN = "%PERSON2_PRONOUN%"
KEY_PERSON2_PERSONAL = "%PERSON2_PERSONAL%"

KEY_CHILD_NAME = "%CHILD_NAME%"
KEY_CHILD_PRONOUN = "%CHILD_NAME%"
KEY_CAREGIVER_NAME = "%CAREGIVER_NAME%"
KEY_CAREGIVER_PRONOUN = "%CAREGIVER_PRONOUN%"

# Classes
class FamilyDyad():

    def __init__(self, group):
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


    def get_caregiver_name(self):
        return self.parent.name


    def get_child_name(self):
        return self.child.name


    def get_target_strings(self):
        if self.target_strings == None:
            self.target_strings = self.__compute_target_strings()
        return self.target_strings

    @staticmethod
    def is_family(group):
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
            KEY_PERSON1_NAME: self.child.name,
            KEY_PERSON1_PERSONAL: self.child_membership.pronoun.personal,
            KEY_PERSON1_PRONOUN: self.child_membership.pronoun.pronoun,
            KEY_PERSON2_NAME: self.parent.name,
            KEY_PERSON2_PERSONAL: self.parent_membership.pronoun.personal,
            KEY_PERSON2_PRONOUN: self.parent_membership.pronoun.pronoun
        }