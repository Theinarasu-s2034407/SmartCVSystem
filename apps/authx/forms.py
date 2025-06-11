from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserCreation(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name','last_name','username', 'email', 'password')  # 自定义用户模型字段

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=100)
    password = forms.CharField(label='password', widget=forms.PasswordInput)