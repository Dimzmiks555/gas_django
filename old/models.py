# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ActOffers(models.Model):
    offer_id = models.IntegerField(blank=True, null=True)
    act_id = models.IntegerField(blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'act_offers'


class Acts(models.Model):
    object = models.ForeignKey('Objects', models.DO_NOTHING, blank=True, null=True)
    application_id = models.IntegerField(blank=True, null=True)
    contract_id = models.IntegerField(blank=True, null=True)
    total = models.FloatField(blank=True, null=True)
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.
    positions = models.TextField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'acts'


class AppMasters(models.Model):
    application = models.ForeignKey('Applications', models.DO_NOTHING, blank=True, null=True)
    master = models.ForeignKey('Masters', models.DO_NOTHING, blank=True, null=True)
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'app_masters'


class Applications(models.Model):
    object = models.ForeignKey('Objects', models.DO_NOTHING, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    reason = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    service = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'applications'


class Calls(models.Model):
    object = models.ForeignKey('Objects', models.DO_NOTHING, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    stage = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'calls'


class Contracts(models.Model):
    object = models.ForeignKey('Objects', models.DO_NOTHING, blank=True, null=True)
    number = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.
    positions = models.TextField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    summ = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contracts'


class Devices(models.Model):
    type = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    device = models.CharField(max_length=255, blank=True, null=True)
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'devices'


class Masters(models.Model):
    application_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'masters'


class ObjectDevices(models.Model):
    device = models.ForeignKey(Devices, models.DO_NOTHING, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    modification = models.CharField(max_length=255, blank=True, null=True)
    device_name = models.CharField(max_length=255, blank=True, null=True)
    object = models.ForeignKey('Objects', models.DO_NOTHING, blank=True, null=True)
    serial = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    date_of_check = models.DateTimeField(blank=True, null=True)
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.
    exploitation = models.CharField(max_length=255, blank=True, null=True)
    date_of_enter = models.DateTimeField(blank=True, null=True)
    brend = models.CharField(max_length=255, blank=True, null=True)
    in_room = models.CharField(max_length=255, blank=True, null=True)
    groove = models.CharField(max_length=255, blank=True, null=True)
    center_to_center = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'object_devices'


class Objects(models.Model):
    for_delete = models.IntegerField(blank=True, null=True)
    type_of_building = models.CharField(max_length=255, blank=True, null=True)
    type_of_city = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True)
    area = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    house = models.CharField(max_length=255, blank=True, null=True)
    room = models.IntegerField(blank=True, null=True)
    passport_serial = models.CharField(max_length=255, blank=True, null=True)
    passport_number = models.CharField(max_length=255, blank=True, null=True)
    passport_getted_by = models.CharField(max_length=255, blank=True, null=True)
    passport_getted_date = models.DateTimeField(blank=True, null=True)
    birthday_date = models.DateTimeField(blank=True, null=True)
    birthday_place = models.CharField(max_length=255, blank=True, null=True)
    show_part = models.IntegerField(blank=True, null=True)
    registration_adress = models.CharField(max_length=255, blank=True, null=True)
    folder = models.IntegerField(blank=True, null=True)
    client = models.CharField(max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=255, blank=True, null=True)
    gas_date = models.DateTimeField(blank=True, null=True)
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.
    street_type = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'objects'


class Offers(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'offers'


class People(models.Model):
    object = models.ForeignKey(Objects, models.DO_NOTHING, blank=True, null=True)
    main = models.IntegerField(blank=True, null=True)
    male = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    sur_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    phone_1 = models.CharField(max_length=255, blank=True, null=True)
    phone_2 = models.CharField(max_length=255, blank=True, null=True)
    phone_3 = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=255, blank=True, null=True)
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'people'


class Scans(models.Model):
    object = models.ForeignKey(Objects, models.DO_NOTHING, blank=True, null=True)
    src = models.CharField(max_length=255, blank=True, null=True)
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'scans'


class Users(models.Model):
    login = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=255, blank=True, null=True)
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'users'
