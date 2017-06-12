from django.db import models
from people.models import Person
from datetime import datetime

DEFAULT_START_DATE = datetime(2017, 5, 1, 0, 0)

class Account(models.Model):
    MEMBERSHIP_STRING = "{0} connected to {1}"
    fullname = models.CharField(max_length=200)
    user_id = models.CharField(max_length=50, unique=True)
    access_token = models.CharField(max_length=1000)
    refresh_token = models.CharField(max_length=1000)
    expires_at = models.DateTimeField(blank=True, null=True)
    person = models.ForeignKey(Person, blank=True, null=True)
    last_pull_time = models.DateTimeField(blank=True, null=True, default=DEFAULT_START_DATE)
    device_version = models.CharField(max_length=64)
    
    def __str__(self):
        person_name = "none"
        if self.person:
            person_name = self.person.name 
        return Account.MEMBERSHIP_STRING.format(self.fullname, person_name)
        
    def set_expires_at_in_unix (self, unixtime):
        """
        Sets token's expiration time using a Unix time
        """
        datetime_in_iso = datetime.fromtimestamp(unixtime)
        self.expires_at = datetime_in_iso.isoformat()
        
    def get_expires_at(self):
        """
        Return token's expiration time in Unix time
        """
        return self.expires_at.strftime("%s")