from django.urls import path
from . import views

urlpatterns = [
    path('analyze-douyin/', views.analyze_douyin, name='analyze_douyin'),
    path('analyze-pose/', views.analyze_pose, name='analyze_pose'),
]

