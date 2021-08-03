from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from core.models import Task


class TaskSerializer(serializers.ModelSerializer):
    """Serialize a Task"""
    class Meta:
        model = Task
        fields = (
            'task_id', 'title', 'description', 'task_status', 'user'
        )
        read_only_fields = ('user',)

    def create(self, validated_data):
        """Create a new task and return it"""
        return Task.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update Task"""
        task = super().update(instance, validated_data)
        return task


