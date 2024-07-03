from django.shortcuts import render

# Create your views here.
from .models import Objects, People, ObjectDevices
from gas.models import Object, Passport, Client, ObjectDevice, DeviceKind, DeviceManufacter, DeviceModel, DeviceModification, DeviceType

def imp(request):
    old_objs = Objects.objects.using('import').all()

    for obj in old_objs:
        print(obj)
        print(obj.id)
        
        new_object = Object.objects.create(
            type_of_building = obj.type_of_building,
            region = obj.region,
            area = obj.area,
            type_of_city = obj.type_of_city,
            city = obj.city,
            street_type = obj.street_type,
            street = obj.street,
            house = obj.house,
            room = obj.room,
            postcode = obj.postcode,
            show_part = None,
            comment = obj.description
        )

        new_passport = Passport.objects.create(
            serial = obj.passport_serial,
            passport_number = obj.passport_number,
            getted_by = obj.passport_getted_by,
            division = None,
            getted_date = obj.passport_getted_date,
            birthday_date = obj.birthday_date,
            birthday_place = obj.birthday_place,
            registration_adress = obj.registration_adress,
            object = new_object,
        )

        old_people = People.objects.using('import').filter(object=obj)

        for p in old_people:
            Client.objects.create(
                firstname = p.first_name,
                lastname = p.sur_name,
                middlename = p.last_name,
                is_main = p.main,
                role = p.role,
                sex = p.male,
                phone_number_1 = p.phone_1,
                phone_number_2 = p.phone_2 or '',
                phone_number_3 = p.phone_3 or '',
                object = new_object,
            )

        old_objdevices = ObjectDevices.objects.using('import').filter(object=obj)
        print(old_objdevices)

        for device in old_objdevices:

            device_type = DeviceType.objects.filter(name__contains=device.device_name.strip())[0]
            device_model = DeviceModel.objects.filter(name__contains=device.model.strip())[0] if device.model and device.model != 'нет' else None
            device_kind = DeviceKind.objects.filter(name__contains=device.type.strip())[0] if device.type and device.type != 'нет' else None
            device_manufacter = DeviceManufacter.objects.filter(name__contains=device.brend.strip())[0] if device.brend and device.brend != 'нет' else None
            device_modification = DeviceModification.objects.filter(name__contains=device.modification.strip())[0] if device.modification and device.modification != 'нет' else None
            
            ObjectDevice.objects.create(
                type = device_type,
                model = device_model,
                modification = device_modification,
                kind = device_kind,
                manufacter = device_manufacter,
                sn = device.serial,
                object = new_object,
            )

    
    pass

