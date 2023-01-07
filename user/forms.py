from django.contrib.auth import forms
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(max_length=64)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
