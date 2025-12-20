from django.contrib import admin
from .models import WorkoutHistory

@admin.register(WorkoutHistory)
class WorkoutHistoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)

