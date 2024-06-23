from django.shortcuts import render
from django.views.generic import CreateView, ListView, DetailView, View, TemplateView
from .models import Object
from .forms import LoginUserForm, ObjectCreateForm, PassportCreateForm, ClientCreateForm, PhoneCreateForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
import datetime






class Login(LoginView):
    form_class = LoginUserForm
    template_name = "login.html"

def Index(request):
    return redirect('/objects')

class ObjectListView(LoginRequiredMixin, ListView):
    template_name = "app/object/list.html"
    model = Object
    extra_context = {
        'total': Object.objects.count(),
    }

    def get_queryset(self):
        return Object.objects.filter()


class ObjectCreateView(LoginRequiredMixin, TemplateView):
    template_name = "app/object/create.html"
    extra_context = {
        'object_form': ObjectCreateForm,
        'passport_form': PassportCreateForm,
        'phone_form': PhoneCreateForm,
        'client_form' : ClientCreateForm
    }

    def post():
        pass
        


class ObjectEditView(LoginRequiredMixin, DetailView):
    model = Object
    pk_url_kwarg = 'id'
    template_name = "app/object/edit.html"