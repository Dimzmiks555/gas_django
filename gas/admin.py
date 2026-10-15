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

from django import forms
from .models import Act
from .act_documents import prepare_revision, store_revision


class ActAdminForm(forms.ModelForm):
    class Meta:
        model = Act
        fields = '__all__'

    def clean(self):
        data = super().clean()
        if self.instance.pk and data.get('date_of_act') and 'master' in data:
            original = Act.objects.get(pk=self.instance.pk)
            master = data['master']
            if original.date_of_act != data['date_of_act'] or original.master_id != (master.pk if master else None):
                self.prepared_document = prepare_revision(original, data['date_of_act'], master)
        return data


@admin.register(Act)
class ActAdmin(admin.ModelAdmin):
    form = ActAdminForm
    list_display = ('act_number', 'object', 'date_of_act', 'master', 'total', 'is_posted', 'to_edit')
    list_filter = ('is_posted', 'to_edit', 'master')
    search_fields = ('act_number', 'object__id')
    readonly_fields = ('uuid_number', 'object', 'act_number', 'total', 'revision', 'document_file')

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        if hasattr(form, 'prepared_document'):
            store_revision(obj, form.prepared_document)
        obj.revision += 1
        super().save_model(request, obj, form, change)
