from rest_framework import serializers
from .models import WorkoutPlan, WorkoutLog, WorkoutExercise

class WorkoutExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutExercise
        fields = ['id', 'name', 'total_sets', 'reps_per_set', 'current_sets', 'tips', 'start_time', 'end_time', 'seconds', 'gif_url', 'category', 'muscle_group', 'order']

class WorkoutPlanSerializer(serializers.ModelSerializer):
    exercises = WorkoutExerciseSerializer(many=True, required=False)
    
    class Meta:
        model = WorkoutPlan
        fields = ['id', 'title', 'created_at', 'is_default', 'exercises']

    def create(self, validated_data):
        exercises_data = validated_data.pop('exercises', [])
        plan = WorkoutPlan.objects.create(**validated_data)
        
        # 获取模型的所有有效字段名
        model_fields = [f.name for f in WorkoutExercise._meta.get_fields()]
        
        for exercise_data in exercises_data:
            # 过滤掉不在模型中的字段，增强鲁棒性
            valid_fields = {k: v for k, v in exercise_data.items() if k in model_fields}
            WorkoutExercise.objects.create(plan=plan, **valid_fields)
        return plan

    def update(self, instance, validated_data):
        exercises_data = validated_data.pop('exercises', None)
        
        # Update plan basic info
        instance.title = validated_data.get('title', instance.title)
        instance.is_default = validated_data.get('is_default', instance.is_default)
        instance.save()

        # 获取模型的所有有效字段名
        model_fields = [f.name for f in WorkoutExercise._meta.get_fields()]

        # Update exercises if provided
        if exercises_data is not None:
            instance.exercises.all().delete()
            for exercise_data in exercises_data:
                valid_fields = {k: v for k, v in exercise_data.items() if k in model_fields}
                WorkoutExercise.objects.create(plan=instance, **valid_fields)
        
        return instance

class WorkoutLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutLog
        fields = '__all__'
