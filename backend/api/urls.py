from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'history', views.WorkoutHistoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('analyze-douyin/', views.analyze_douyin, name='analyze_douyin'),
    path('analyze-pose/', views.analyze_pose, name='analyze_pose'),
    path('analyze-video/', views.analyze_video_content, name='analyze_video'),
]

