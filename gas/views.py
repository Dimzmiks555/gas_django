from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from .models import Object
from .forms import LoginUserForm
from django.contrib.auth.views import LoginView


class Login(LoginView):
    form_class = LoginUserForm
    template_name = "login.html"


class ObjectListView(ListView):
    template_name = "app/object/list.html"
    model = Object

    def get_queryset(self):
        return Object.objects.filter()



class ObjectCreateView(TemplateView):
    template_name = "app/object/create.html"

class ObjectEditView(DetailView):
    model = Object
    pk_url_kwarg = 'id'
    template_name = "app/object/edit.html"