# Generated by Django 5.0.4 on 2024-06-30 20:11

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceKind',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Название')),
            ],
        ),
        migrations.CreateModel(
            name='DeviceManufacter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Название')),
            ],
        ),
        migrations.CreateModel(
            name='DeviceModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Название')),
            ],
        ),
        migrations.CreateModel(
            name='DeviceModification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Название')),
            ],
        ),
        migrations.CreateModel(
            name='DeviceType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Название')),
            ],
        ),
        migrations.CreateModel(
            name='Master',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=256, verbose_name='Имя')),
                ('lastname', models.CharField(max_length=256, verbose_name='Фамилия')),
                ('middlename', models.CharField(max_length=256, verbose_name='Отчество')),
            ],
        ),
        migrations.CreateModel(
            name='Object',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_of_building', models.CharField(choices=[('Дом', 'Дом'), ('Квартира', 'Квартира')], max_length=255, verbose_name='Тип домовладения')),
                ('region', models.CharField(max_length=255, verbose_name='Область')),
                ('area', models.CharField(max_length=255, verbose_name='Район')),
                ('type_of_city', models.CharField(max_length=255, verbose_name='Тип населенного пункта')),
                ('city', models.CharField(max_length=255, verbose_name='Город')),
                ('street_type', models.CharField(max_length=255, verbose_name='Тип улицы')),
                ('street', models.CharField(max_length=255, verbose_name='Улица')),
                ('house', models.CharField(max_length=255, verbose_name='Дом')),
                ('room', models.CharField(blank=True, max_length=255, verbose_name='Квартира')),
                ('postcode', models.CharField(blank=True, max_length=50, verbose_name='Индекс')),
                ('show_part', models.BooleanField(blank=True, null=True, verbose_name='Отображать часть дома/квартиру в документах')),
                ('gas_date', models.DateField(blank=True, null=True, verbose_name='Дата пуска газа')),
                ('comment', models.TextField(blank=True, verbose_name='Примечание')),
            ],
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contract_number', models.IntegerField(unique=True, verbose_name='Номер')),
                ('status', models.CharField(max_length=50, verbose_name='Статус')),
                ('date_of_contract', models.DateField(default=datetime.datetime(2024, 6, 30, 23, 11, 3, 851640), verbose_name='Дата')),
                ('summ', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Сумма')),
                ('object', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='gas.object')),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=256, verbose_name='Имя')),
                ('lastname', models.CharField(max_length=256, verbose_name='Фамилия')),
                ('middlename', models.CharField(max_length=256, verbose_name='Отчество')),
                ('is_main', models.BooleanField(default=True, verbose_name='Ответственное лицо?')),
                ('role', models.CharField(default='Собственник', max_length=256, verbose_name='Роль')),
                ('sex', models.CharField(choices=[('woman', 'Женский'), ('man', 'Мужской')], max_length=20, verbose_name='Пол')),
                ('phone_number_1', models.CharField(max_length=256, verbose_name='Номер телефона 1')),
                ('phone_number_2', models.CharField(blank=True, max_length=256, null=True, verbose_name='Номер телефона 2')),
                ('phone_number_3', models.CharField(blank=True, max_length=256, null=True, verbose_name='Номер телефона 3')),
                ('object', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gas.object', verbose_name='Объект')),
            ],
        ),
        migrations.CreateModel(
            name='ObjectDevice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sn', models.CharField(max_length=256, verbose_name='Серийный номер')),
                ('date_of_manufacture', models.DateField(default=datetime.datetime(2024, 6, 30, 23, 11, 3, 852641), verbose_name='Дата изготовления')),
                ('date_of_commissioning', models.DateField(default=datetime.datetime(2024, 6, 30, 23, 11, 3, 852641), verbose_name='Дата ввода в эксплуатацию')),
                ('kind', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gas.devicekind', verbose_name='Тип')),
                ('manufacter', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gas.devicemanufacter', verbose_name='Производитель')),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gas.devicemodel', verbose_name='Модель')),
                ('modification', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gas.devicemodification', verbose_name='Модификация')),
                ('object', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='gas.object')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gas.devicetype', verbose_name='Категория оборудования')),
            ],
        ),
        migrations.CreateModel(
            name='Passport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial', models.CharField(max_length=12, verbose_name='Серия')),
                ('passport_number', models.CharField(max_length=12, verbose_name='Номер')),
                ('getted_by', models.CharField(max_length=255, verbose_name='Выдан')),
                ('getted_date', models.DateField(verbose_name='Дата выдачи')),
                ('division', models.CharField(max_length=255, verbose_name='Код подразделения')),
                ('birthday_date', models.DateField(verbose_name='День рождения')),
                ('birthday_place', models.CharField(max_length=255, verbose_name='Место рождения')),
                ('registration_adress', models.CharField(max_length=255, verbose_name='Адрес регистрации')),
                ('object', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='gas.object', verbose_name='Объект')),
            ],
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Название')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gas.devicetype', verbose_name='Тип оборудования')),
            ],
        ),
    ]
