from rest_framework import serializers
from .models import Event, Category
from users.serializers import UserSerializer, User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']

class EventSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    creator = UserSerializer(read_only=True)
    participants = UserSerializer(many=True)

    class Meta: 
        model = Event
        fields = ['title', 'description', 'start_time', 'creator', 'participants', 'address', 'category']

class EventCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="name", queryset=Category.objects.all())
    creator = serializers.PrimaryKeyRelatedField(read_only=True)
    participants = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)

    class Meta: 
        model = Event
        fields = ['title', 'description', 'start_time', 'creator', 'participants', 'address', 'category']

    def create(self, validated_data):
        user = self.context['request'].user
        category_name = validated_data.pop("category")
        participants = validated_data.pop('participants', [])

        category, _ = Category.objects.get_or_create(name=category_name)

        event = Event.objects.create(
            creator = user,
            category=category,
            **validated_data
        )

        if participants:
            event.participants.set(participants)
            
        return event
        