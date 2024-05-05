
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django import forms




class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Логин'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Пароль'}))
 