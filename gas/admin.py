from django.contrib import admin

# Register your models here.
from .models import Master, Contract, Phone, Client, Passport, Object

admin.site.register(Master)
admin.site.register(Contract)
admin.site.register(Phone)
admin.site.register(Client)
admin.site.register(Passport)
admin.site.register(Object)