from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'plans', views.WorkoutPlanViewSet)
router.register(r'logs', views.WorkoutLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('analyze-douyin/', views.analyze_douyin, name='analyze_douyin'),
    path('analyze-pose/', views.analyze_pose, name='analyze_pose'),
    path('analyze-video/', views.analyze_video_content, name='analyze_video'),
    path('evaluate-complete-training/', views.evaluate_complete_training, name='evaluate_complete_training'),
]
