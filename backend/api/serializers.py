from rest_framework import serializers
from .models import WorkoutHistory

class WorkoutHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutHistory
        fields = '__all__'

