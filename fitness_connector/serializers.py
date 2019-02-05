from rest_framework import serializers

class PersonFitnessSyncResultSerializer(serializers.Serializer):
    person_id = serializers.IntegerField()
    last_pull_time = serializers.DateTimeField()