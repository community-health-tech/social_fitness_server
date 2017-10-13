from rest_framework import serializers

from challenges.models import PersonChallenge


class AvailableChallengeSerializer(serializers.Serializer):
    option = serializers.IntegerField()
    goal = serializers.IntegerField()
    unit = serializers.CharField(max_length=32)
    unit_duration = serializers.CharField(max_length=32)
    total_duration = serializers.CharField(max_length=32)
    text = serializers.CharField(max_length=128, allow_blank=True, required=False)
    level_id = serializers.IntegerField()


class ListOfAvailableChallengestSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=128)
    subtext = serializers.CharField(max_length=128)
    level_order = serializers.IntegerField()
    challenges = AvailableChallengeSerializer(many=True)


class PersonChallengeSerializer(serializers.ModelSerializer):
    person_id = serializers.SerializerMethodField()
    goal = serializers.SerializerMethodField()

    class Meta:
        model = PersonChallenge
        fields = ('person_id', 'goal', 'unit', 'unit_duration')

    def get_person_id(self, obj): return (obj.person.id)

    def get_goal(self, obj): return (obj.unit_goal)


class CurrentChallengeSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=64)
    subtext = serializers.CharField(max_length=64)
    total_duration = serializers.CharField(max_length=32)
    start_datetime = serializers.DateTimeField()
    end_datetime = serializers.DateTimeField()
    level_id = serializers.IntegerField()
    level_order = serializers.IntegerField()
    progress = PersonChallengeSerializer(many=True)
