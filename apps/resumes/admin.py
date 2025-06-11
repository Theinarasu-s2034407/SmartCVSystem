from django.contrib import admin

from apps.resumes.models import Resume, Skill

# Register your models here.
admin.site.register(Resume)
admin.site.register(Skill)