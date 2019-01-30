from rest_framework import serializers
from story_manager.models import Story, GroupStory


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ('id', 'title', 'cover_url', 'def_url')


class GroupStorySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="story.id")
    title= serializers.ReadOnlyField(source="story.title")
    cover_url = serializers.ReadOnlyField(source="story.cover_url")
    def_url = serializers.ReadOnlyField(source="story.def_url")
    is_locked = serializers.ReadOnlyField(source="story.is_locked")
    next_story_id = serializers.ReadOnlyField(source="story.next_story_id")

    class Meta:
        model = GroupStory
        fields = ('id', 'title', 'cover_url', 'def_url', 'is_current',
                  'current_page', 'is_locked', 'next_story_id')

    def update(self, instance, validated_data):
        instance.is_current = validated_data.get('is_current', instance.is_current)
        instance.current_page = validated_data.get('current_page', instance.current_page)
        instance.save()
        return instance


class GroupStoryListSerializer(serializers.Serializer):
    current_story_id = serializers.ReadOnlyField()
    stories = GroupStorySerializer(many=True, read_only=True)
