
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django import forms
from .models import Object, Passport, Client, Contract, ObjectDevice
import datetime





class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Логин'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Пароль'}))
 
class ObjectCreateForm(forms.ModelForm):
    class Meta:
        model = Object
        fields = ['type_of_building','region','area','type_of_city','city','street_type','street','house','room','postcode','comment']
        
 
class PassportCreateForm(forms.ModelForm):
    getted_date = forms.DateField(label='Дата выдачи',widget=forms.SelectDateWidget(years=range(1924, datetime.datetime.today().year + 1)))
    birthday_date = forms.DateField(label='Дата рождения',widget=forms.SelectDateWidget(years=range(1924, datetime.datetime.today().year + 1)))
    class Meta:
        model = Passport
        fields = ['serial','passport_number','getted_by','getted_date','division','birthday_date','birthday_place','registration_adress']
 
# class ClientCreateForm(forms.ModelForm):
#     class Meta:
#         model = Client
#         fields = ['firstname','lastname','middlename','is_main','role','sex']
 

class ContractCreateForm(forms.ModelForm):
    date = forms.DateField(label='Дата',widget=forms.SelectDateWidget(years=range(2024, 2050)))
    class Meta:
        model = Contract
        fields = ['contract_number', 'date']


ObjectDeviceFormSet = forms.modelformset_factory(
    ObjectDevice, 
    fields=(
        "type", 
        "model",
        "kind", 
        "modification", 
        "manufacter", 
        "sn", 
        "date_of_manufacture", 
        "date_of_commissioning"
        ), 
    extra=1
)
 
ClientFormSet = forms.modelformset_factory(
    Client, fields=('lastname', 'firstname','middlename','is_main','role','sex','phone_number_1','phone_number_2','phone_number_3'), extra=1
)
 