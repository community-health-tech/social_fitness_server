from django.db import models


class Person(models.Model):
    name = models.CharField(max_length=200)
    birth_date = models.DateField()
    
    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(Person, through='Membership')
    
    def __str__(self):
        return self.name


class Membership(models.Model):
    MEMBERSHIP_STRING = "{0} ({1} of {2})"
    GROUP_ROLE = (
        ('P', 'Parent'),
        ('C', 'Child'),
    )
        
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    role = models.CharField(max_length=1, choices=GROUP_ROLE)
    
    def __str__(self):
        return Membership.MEMBERSHIP_STRING.format(self.person.name, 
            self.get_role_display(), self.group.name)
