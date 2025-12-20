from django.contrib import admin
from .models import WorkoutPlan, WorkoutLog, WorkoutExercise

class WorkoutExerciseInline(admin.TabularInline):
    model = WorkoutExercise
    extra = 1

@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_default', 'created_at')
    search_fields = ('title',)
    list_filter = ('is_default',)
    inlines = [WorkoutExerciseInline]

@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan', 'total_sets', 'reps_per_set', 'order')
    list_filter = ('plan',)
    search_fields = ('name', 'plan__title')

@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    list_display = ('plan_title', 'start_time', 'duration', 'status', 'ai_score')
    list_filter = ('status', 'start_time')
    search_fields = ('plan_title',)
