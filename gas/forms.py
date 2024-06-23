
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django import forms
from .models import Object, Passport, Client, Phone
import datetime





class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Логин'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Пароль'}))
 
class ObjectCreateForm(forms.ModelForm):
    class Meta:
        model = Object
        fields = ['type_of_building','region','area','type_of_city','city','street_type','street','house','room','postcode','show_part','comment']
        
 
class PassportCreateForm(forms.ModelForm):
    getted_date = forms.DateField(label='Дата выдачи',widget=forms.SelectDateWidget(years=range(1924, datetime.datetime.today().year + 1)))
    birthday_date = forms.DateField(label='Дата рождения',widget=forms.SelectDateWidget(years=range(1924, datetime.datetime.today().year + 1)))
    class Meta:
        model = Passport
        
        fields = '__all__'
 
class ClientCreateForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'
 
class PhoneCreateForm(forms.ModelForm):
    class Meta:
        model = Phone
        fields = ['number']
 