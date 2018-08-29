from django.db import models
from django.contrib.auth.models import User

# CONSTANTS
ROLE_PARENT = "P"
ROLE_CHILD = "C"
ROLE_FRIEND= "F"
ROLE_NONE = "N"

GROUP_ROLE = (
    (ROLE_PARENT, 'Parent'),
    (ROLE_CHILD, 'Child'),
    (ROLE_FRIEND, 'Friend'),
    (ROLE_CHILD, 'None'),
)

DEFAULT_PERSON_META_PROFILE_JSON_STRING = "{\"bio\": \"insert bio here\"}"  # type: str

# MODELS


class Person(models.Model):
    name = models.CharField(max_length=200)
    birth_date = models.DateField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None,
                                null=True, blank=True)
    
    def __str__(self):
        return self.name

    def get_meta(self):
        # type: () -> PersonMeta
        if PersonMeta.objects.filter(person=self).exists():
            return PersonMeta.objects.filter(person=self).first()
        else:
            person_meta = PersonMeta()  # type PersonMeta
            person_meta.person = self
            person_meta.profile_json = DEFAULT_PERSON_META_PROFILE_JSON_STRING
            return person_meta


    def set_meta_profile(self, json_string):
        # type: (str) -> None
        if PersonMeta.objects.filter(person=self).exists():
            person_meta = PersonMeta.objects.filter(person=self).first()
            person_meta.profile_json = json_string
        else:
            person_meta = PersonMeta.objects.create(person=self, profile_json=json_string)
        person_meta.save()


class PersonMeta(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    profile_json = models.TextField()

    def __str__(self):
        return self.person.name


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


class Circle(models.Model):
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(Person, through='CircleMembership')

    def __str__(self):
        return self.name


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
                                                   self.get_role_display(),
                                                   self.group.name)

    @staticmethod
    def is_member(group, person_id):
        # type: (Group, int) -> bool
        return Membership.objects.filter(group=group, person__id=person_id).exists()

    @staticmethod
    def get_member(group, person_id):
        # type: (Group, int) -> Person
        membership = Membership.objects.filter(group=group, person__id=person_id).first() # type: Membership
        return membership.person


class CircleMembership(models.Model):
    MEMBERSHIP_STRING = "{0} of {1}"

    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE)

    def __str__(self):
        return CircleMembership.MEMBERSHIP_STRING.format(self.person.name,
                                                         self.circle.name)