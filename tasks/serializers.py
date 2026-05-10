from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    is_urgent = serializers.SerializerMethodField()
    formatted_deadline = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id',
            'owner',
            'title',
            'category',
            'description',
            'priority',
            'status',
            'start_time',
            'end_time',
            'deadline',
            'duration',
            'actual_duration',
            'created_at',
            'updated_at',
            'is_urgent',
            'formatted_deadline',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at', 'is_urgent', 'formatted_deadline']

    def get_is_urgent(self, obj):
        return obj.is_urgent()

    def get_formatted_deadline(self, obj):
        return obj.deadline.strftime('%Y-%m-%d %H:%M')
