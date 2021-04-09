from rest_framework import serializers
from fitness.models import ActivityByDay


class PersonActivityByDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityByDay
        fields = ("date", "steps", "calories", "distance")


class PersonFitnessSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    last_pull_time = serializers.DateTimeField()
    role = serializers.CharField(max_length=2)
    activities = PersonActivityByDaySerializer(many=True, read_only=True)


class GroupFitnessSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    activities = PersonFitnessSerializer(many=True, read_only=True)