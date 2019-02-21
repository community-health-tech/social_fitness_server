from rest_framework import serializers

class PersonFitnessSyncResultSerializer(serializers.Serializer):
    person_id = serializers.IntegerField()
    last_sync_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%f%z")
    #last_sync_time = serializers.DateTimeField()