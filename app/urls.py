"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include  
from gas.views import Index, ObjectCreateView, ObjectIdView, ObjectListView, ContractCreateView, ActCreateFromContractView, ToEditObject, EditCommentObject, AddContactView
from old.views import imp

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", Index),
    path("import/", imp),
    path("accounts/", include("django.contrib.auth.urls")),  # new
    path("objects/", ObjectListView.as_view()),
    path("objects/<int:id>", ObjectIdView.as_view()),
    path("objects/<int:id>/to_edit", ToEditObject),
    path("objects/<int:id>/edit_comment", EditCommentObject),
    path("objects/<int:id>/add_contact", AddContactView.as_view()),
    path("objects/<int:id>/contract/create", ContractCreateView.as_view()),
    path("objects/<int:id>/act/create_from_contract", ActCreateFromContractView.as_view()),
    path("objects/create/", ObjectCreateView.as_view()),
    # path('', include('pwa.urls'))

]
