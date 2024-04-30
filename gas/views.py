from django.shortcuts import render
from django.views.generic import TemplateView


class LoginView(TemplateView):
    template_name = "login.html"




class ObjectListView(TemplateView):
    template_name = "app/object/list.html"

class ObjectCreateView(TemplateView):
    template_name = "app/object/create.html"

class ObjectEditView(TemplateView):
    template_name = "app/object/edit.html"