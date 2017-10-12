from django.db import models
from django.contrib.auth.models import User

# CONSTANTS
ROLE_PARENT = "P"
ROLE_CHILD = "C"

GROUP_ROLE = (
    (ROLE_PARENT, 'Parent'),
    (ROLE_CHILD, 'Child'),
)

# MODELS
class Person(models.Model):
    name = models.CharField(max_length=200)
    birth_date = models.DateField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None,
                                null=True, blank=True)
    
    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(Person, through='Membership')
    
    def __str__(self):
        return self.name

    def get_person_by_role(self, role):
        for person in self.activities:
            if person.role == role :
                person_of_interest = person
                return person_of_interest
        raise Exception("No Person of that role")


class Pronoun(models.Model):
    MEMBERSHIP_STRING = "{0}, {1}, {2}"

    personal = models.CharField(max_length=16, default="personal")
    pronoun = models.CharField(max_length=16, default="pronoun")
    possessive = models.CharField(max_length=16, default="possessive")

    def __str__(self):
        return Pronoun.MEMBERSHIP_STRING.format(
            self.personal,
            self.pronoun,
            self.possessive
        )


class Membership(models.Model):
    MEMBERSHIP_STRING = "{0} ({1} of {2})"
        
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    role = models.CharField(max_length=1, choices=GROUP_ROLE)
    pronoun = models.ForeignKey(Pronoun, on_delete=models.CASCADE, default=1)
    
    def __str__(self):
        return Membership.MEMBERSHIP_STRING.format(self.person.name, 
            self.get_role_display(), self.group.name)