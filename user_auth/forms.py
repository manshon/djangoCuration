from django import forms
from user_auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserForm(UserCreationForm):

    class Meta:
        model = User
        fields = (
            'username',
            'password1',  # password
            'password2',  # password_confirm
        )