from django.urls import path
from .views import  *
app_name = "resumes"

urlpatterns = [
    path("candidates/", ResumeView.get_candidates, name="resumes_candidates"),
    path("applications/", ResumeView.get_applications, name="resumes_applications"),
]