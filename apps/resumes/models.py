from django.db import models
from apps.jobposts.models import JobPost  # Assuming you have a JobPost model in jobposts app

# Create your models here.
class Candidate(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    linkedin_profile = models.URLField(max_length=255, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    notice_period = models.CharField(max_length=50, blank=True, null=True)
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Application(models.Model):
    id = models.AutoField(primary_key=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='applications')  # Assuming a Job model exists
    company_name = models.CharField(max_length=255)
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[
        ('applied', 'Applied'),
        ('interviewed', 'Interviewed'),
        ('offered', 'Offered'),
        ('rejected', 'Rejected')
    ], default='applied')
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)  # Assuming resumes are uploaded as files
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)  # Assuming this is a username

class CVExtraction(models.Model):
    id = models.AutoField(primary_key=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='cv_extractions')
    extracted_data = models.JSONField()  # Assuming you store extracted data as JSON
    created_at = models.DateTimeField(auto_now_add=True)