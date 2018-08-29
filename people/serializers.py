from django.db.models.query import QuerySet
from rest_framework import serializers
from people.models import Person, Group, Membership, Circle, CircleMembership, PersonMeta
from fitness_connector.models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('user_id', 'last_pull_time', 'device_version')


class PersonSerializer(serializers.ModelSerializer):
    account = serializers.SerializerMethodField()
    profile_json = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = ('id', 'name', 'account', 'profile_json')

    def get_account(self, obj):
        account = Account.objects.filter(person__id=obj.id)

        if account.exists():
            serialized = AccountSerializer(account.first())
            return serialized.data
        else:
            return None

    def get_profile_json(self, obj):
        person_meta = PersonMeta.objects.filter(person__id=obj.id)

        if person_meta.exists():
            return person_meta.first().profile_json
        else:
            return None


class PersonMetaSerializer(serializers.ModelSerializer):
    profile_json = serializers.JSONField()

    class Meta:
        model = PersonMeta
        fields = ('profile_json',)


class MembershipSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="person.id")
    name = serializers.ReadOnlyField(source="person.name")
    account = serializers.SerializerMethodField()
    profile_json = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = ('id', 'name', 'role', 'account')

    def get_account(self, obj):
        account = Account.objects.filter(person__id=obj.id)

        if account.exists():
            serialized = AccountSerializer(account.first())
            return serialized.data
        else:
            return None

    def get_profile_json(self, obj):
        person_meta = PersonMeta.objects.filter(person__id=obj.id)

        if person_meta.exists():
            return person_meta.first().profile_json
        else:
            return None


class CircleMembershipSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="person.id")
    name = serializers.ReadOnlyField(source="person.name")
    profile_json = serializers.SerializerMethodField()

    class Meta:
        model = CircleMembership
        fields = ('id', 'name')

    def get_profile_json(self, obj):
        person_meta = PersonMeta.objects.filter(person__id=obj.id)

        if person_meta.exists():
            return person_meta.first().profile_json
        else:
            return None


class GroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'members')


class GroupSerializer(serializers.ModelSerializer):
    members = MembershipSerializer(source="membership_set", many=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'members', )


class CircleSerializer(serializers.ModelSerializer):
    members = CircleMembershipSerializer(source="circlemembership_set", many=True)

    class Meta:
        model = Circle
        fields = ('id', 'name', 'members', )
