from django.db import models

# Create your models here.
class JobPost(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    level = models.CharField(max_length=50, choices=[
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('lead', 'Lead Level'),
        ('manager', 'Manager Level'),
        ('director', 'Director Level'),
        ('executive', 'Executive Level')
    ])
    skills = models.TextField()
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, choices=[
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('draft', 'Draft')
    ], default='open')
    expired_date = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)  # Assuming this is a username
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)  # Assuming this is a username
    updated_at = models.DateTimeField(auto_now=True)