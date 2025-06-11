from django import forms
from apps.resumes.models import Resume, Skill


class ResumeFilterForm(forms.Form):
    SKILLS_CHOICES = [
        ('Python', 'Python'),
        ('Django', 'Django'),
        ('SQL', 'SQL'),
        ('JavaScript', 'JavaScript'),
    ]

    skills = forms.MultipleChoiceField(
        choices=SKILLS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    tags = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'label,label,....'}))
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Start date'
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='End Date'
    )
    keyword = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Skill keyword'}),
        label='Skill keyword search'
    )

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        return [tag.strip() for tag in tags.split(',') if tag.strip()]



class ResumeForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter multiple labels separated by commas'})
    )
    skills = forms.ModelMultipleChoiceField(
        queryset= Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Resume
        fields = ['file', 'tags', 'skills']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx'})
        }

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Example: Python',
                'class': 'form-control'
            })
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip().lower()
        if Skill.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("This skill already exists")
        return name.capitalize()