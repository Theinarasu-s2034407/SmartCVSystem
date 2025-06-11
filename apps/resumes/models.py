from django.db import models
from django.contrib.auth.models import User
from django import forms

class Skill(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/%Y/%m/%d/')
    upload_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.CharField(max_length=200, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'upload_date'])
        ]

    def __str__(self):
        return f"{self.user.username}'s Resume"


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': '例如：Python编程',
                'class': 'form-control'
            })
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip().lower()
        if Skill.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("该技能已存在")
        return name.capitalize()

