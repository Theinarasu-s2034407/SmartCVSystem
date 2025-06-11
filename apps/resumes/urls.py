from django.urls import path
from apps.resumes.views import  ResumeListView
from . import views

app_name = "resume"

urlpatterns = [
    path('list/', ResumeListView.as_view(), name='resume-search'),
    path('add_resume/', views.create_resume, name='add_resume'),
    path('add_skill/', views.skill_management, name='add_skill'),
]
