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
from gas.views import Index, ObjectCreateView, ObjectIdView, ObjectListView, ContractCreateView, ActCreateFromContractView, ToEditObject, EditCommentObject, AddContactView, DownloadContractView, DownloadActView
from gas.views import ActEditView, ActListView, ActDetailView, ObjectVisitTypeView
from gas.exports import export_page, export_download
from old.views import imp
from django.conf import settings


urlpatterns = [
    path('export/', export_page, name='export'),
    path('export/<str:kind>/', export_download, name='export-download'),
    path('objects/<int:id>/visit-type/', ObjectVisitTypeView.as_view(), name='object-visit-type'),
    path('acts/', ActListView.as_view(), name='act-list'),
    path('acts/<uuid:act_id>/', ActDetailView.as_view(), name='act-detail'),
    path('objects/<int:object_id>/acts/<uuid:act_id>/', ActEditView.as_view(), name='act-edit'),
    path('admin/', admin.site.urls),
    path("", Index),
    path("import/", imp),
    path('download/contract/<int:id>/', DownloadContractView),
    path('download/act/<str:uuid_number>/', DownloadActView),
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
