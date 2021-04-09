from rest_framework import serializers

from challenges.models import PersonChallenge


class AvailableChallengeSerializer(serializers.Serializer):
    option = serializers.IntegerField(required=False)
    goal = serializers.IntegerField()
    unit = serializers.CharField(max_length=32)
    unit_duration = serializers.CharField(max_length=32)
    total_duration = serializers.CharField(max_length=32)
    start_datetime_utc = serializers.DateTimeField(required=False)
    text = serializers.CharField(max_length=128, allow_blank=True, required=False)
    level_id = serializers.IntegerField()


class AvailableChallengeListField(serializers.ListField):
    child = AvailableChallengeSerializer()


class ListOfAvailableChallengestSerializer(serializers.Serializer):
    is_currently_running = serializers.BooleanField()
    text = serializers.CharField(max_length=128)
    subtext = serializers.CharField(max_length=128)
    total_duration = serializers.CharField(max_length=16)
    start_datetime = serializers.DateTimeField()
    end_datetime = serializers.DateTimeField()
    level_id = serializers.IntegerField()
    level_order = serializers.IntegerField()
    challenges = AvailableChallengeSerializer(many=True)
    challenges_by_person = serializers.DictField(
        child=AvailableChallengeListField())


class IndividualizedGroupChallengeSerializer(serializers.Serializer):
    total_duration = serializers.CharField(max_length=32)
    start_datetime_utc = serializers.DateTimeField(required=False)
    level_id = serializers.IntegerField()
    challenges_by_person = serializers.DictField(
        child=AvailableChallengeSerializer())


class PersonChallengeSerializer(serializers.ModelSerializer):
    person_id = serializers.SerializerMethodField()
    goal = serializers.SerializerMethodField()

    class Meta:
        model = PersonChallenge
        fields = ('person_id', 'goal', 'unit', 'unit_duration')

    def get_person_id(self, obj): return (obj.person.id)

    def get_goal(self, obj): return (obj.unit_goal)


class PersonProgressSerializer(serializers.Serializer):
    person_id = serializers.IntegerField()
    goal = serializers.IntegerField()
    unit = serializers.CharField()
    unit_duration = serializers.CharField()
    progress = serializers.ListField(child=serializers.IntegerField())
    progress_percent = serializers.ListField(child=serializers.FloatField())
    progress_achieved = serializers.ListField(child=serializers.BooleanField())
    total_progress = serializers.IntegerField()


class CurrentChallengeSerializer(serializers.Serializer):
    is_currently_running = serializers.BooleanField()
    text = serializers.CharField(max_length=64)
    subtext = serializers.CharField(max_length=64)
    total_duration = serializers.CharField(max_length=32)
    start_datetime = serializers.DateTimeField()
    end_datetime = serializers.DateTimeField()
    level_id = serializers.IntegerField()
    level_order = serializers.IntegerField()
    # challenges = PersonChallengeSerializer(many=True)
    progress = PersonProgressSerializer(many=True)


class ChallengeViewModelSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=32)
    available = ListOfAvailableChallengestSerializer()
    running = CurrentChallengeSerializer()
    passed = CurrentChallengeSerializer()


class AverageStepsSerializers(serializers.Serializer):
    step_averages = serializers.DictField(child=serializers.IntegerField())