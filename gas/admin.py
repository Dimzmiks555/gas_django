from django.contrib import admin
from django.utils.html import format_html

# Register your models here.
from .models import Master, Contract, Client, Passport, Object, Price, DeviceModel, DeviceType, ObjectDevice, DeviceKind, DeviceManufacter, DeviceModification

admin.site.register(Master)
admin.site.register(Contract)
admin.site.register(Client)
admin.site.register(Passport)
# admin.site.register(Object)
admin.site.register(Price)
admin.site.register(DeviceModel)
admin.site.register(DeviceType)
admin.site.register(DeviceModification)
admin.site.register(DeviceKind)
admin.site.register(DeviceManufacter)
admin.site.register(ObjectDevice)

@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ("get_full_address",  'to_edit_mark', "id", )
    search_fields = ("area", "city", "house", "id", "postcode", "region", "room", "street", "street_type", "type_of_building", "type_of_city")
    list_filter = ("to_edit", )


    def to_edit_mark(self, obj):
        print(obj.to_edit)

        if obj.to_edit:
            return format_html("<b style='color: red'><i>К редактированию</i></b>", obj.to_edit)