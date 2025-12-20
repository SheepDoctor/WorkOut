from django.core.management.base import BaseCommand
from api.models import WorkoutPlan, WorkoutExercise

class Command(BaseCommand):
    help = 'Initialize default workout plans'

    def handle(self, *args, **options):
        # 清除现有默认计划（可选，为了确保更新）
        WorkoutPlan.objects.filter(is_default=True).delete()

        default_plans = []

        for plan_data in default_plans:
            exercises_data = plan_data.pop('exercises')
            plan = WorkoutPlan.objects.create(**plan_data)
            
            for ex_data in exercises_data:
                WorkoutExercise.objects.create(plan=plan, **ex_data)
                
            self.stdout.write(self.style.SUCCESS(f'Successfully created plan: {plan.title}'))


