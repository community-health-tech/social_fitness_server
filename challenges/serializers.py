from rest_framework import serializers

class ChallengeSerializers(serializers.Serializer):
    order = serializers.IntegerField()
    goal = serializers.IntegerField()
    unit = serializers.CharField(max_length=32)
    unit_duration = serializers.CharField(max_length=32)
    total_duration = serializers.CharField(max_length=32)
    text = serializers.CharField(max_length=128)


class AvailableChallengesSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=128)
    subtext = serializers.CharField(max_length=128)
    challenges = ChallengeSerializers(many=True)
