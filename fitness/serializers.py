from rest_framework import serializers
from fitness.models import ActivityByDay
from people.serializers import PersonSerializer


class PersonActivityByDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityByDay
        fields = ("date", "steps", "calories", "distance")


class PersonFitnessSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    last_pull_time = serializers.DateTimeField()
    activities = PersonActivityByDaySerializer(many=True, read_only=True)

class PeopleFitnessSerializer(serializers.Serializer):
    #id = serializers.IntegerField()
    #name = serializers.CharField(max_length=200)
    #last_pull_time = serializers.DateTimeField()
    #activities = PersonActivityByDaySerializer(many=True, read_only=True)

    members = PersonSerializer(many=True, read_only=True)
    activities = PersonFitnessSerializer(many=True, read_only=True)
