from django.shortcuts import render
from django.views.generic import CreateView, ListView, DetailView
from .models import Object
from .forms import LoginUserForm, ObjectCreateForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin




class Login(LoginView):
    form_class = LoginUserForm
    template_name = "login.html"

class ObjectListView(LoginRequiredMixin, ListView):
    template_name = "app/object/list.html"
    model = Object
    extra_context = {
        'total': Object.objects.count(),
    }

    def get_queryset(self):
        return Object.objects.filter()


class ObjectCreateView(LoginRequiredMixin, CreateView):
    template_name = "app/object/create.html"
    form_class = ObjectCreateForm

class ObjectEditView(LoginRequiredMixin, DetailView):
    model = Object
    pk_url_kwarg = 'id'
    template_name = "app/object/edit.html"