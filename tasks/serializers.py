from rest_framework import serializers
from core.models import Task


class TaskSerializer(serializers.ModelSerializer):
    """Serialize a Task"""
    class Meta:
        model = Task
        fields = (
            'task_id', 'title', 'description', 'task_status'
        )
        read_only_fields = ('task_id',)
    
    # def create(self, validated_data):
    #     """Create a new task and return it"""
    #     return Task.objects.create(**validated_data)
