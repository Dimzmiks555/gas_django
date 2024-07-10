# Generated by Django 5.0.4 on 2024-07-02 17:12

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gas', '0003_alter_contract_date_of_contract_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='client',
            options={'verbose_name': 'Клиент', 'verbose_name_plural': 'Клиенты'},
        ),
        migrations.AlterModelOptions(
            name='contract',
            options={'verbose_name': 'Договор', 'verbose_name_plural': 'Договора'},
        ),
        migrations.AlterModelOptions(
            name='devicekind',
            options={'verbose_name': 'Тип оборудования', 'verbose_name_plural': 'Типы оборудования'},
        ),
        migrations.AlterModelOptions(
            name='devicemanufacter',
            options={'verbose_name': 'Производитель оборудования', 'verbose_name_plural': 'Производители оборудования'},
        ),
        migrations.AlterModelOptions(
            name='devicemodel',
            options={'verbose_name': 'Модель оборудования', 'verbose_name_plural': 'Модели оборудования'},
        ),
        migrations.AlterModelOptions(
            name='devicemodification',
            options={'verbose_name': 'Модификация оборудования', 'verbose_name_plural': 'Модификации оборудования'},
        ),
        migrations.AlterModelOptions(
            name='devicetype',
            options={'verbose_name': 'Категория оборудования', 'verbose_name_plural': 'Категории оборудования'},
        ),
        migrations.AlterModelOptions(
            name='master',
            options={'verbose_name': 'Мастер', 'verbose_name_plural': 'Мастера'},
        ),
        migrations.AlterModelOptions(
            name='object',
            options={'verbose_name': 'Объект', 'verbose_name_plural': 'Объекты'},
        ),
        migrations.AlterModelOptions(
            name='objectdevice',
            options={'verbose_name': 'Оборудование', 'verbose_name_plural': 'Оборудования'},
        ),
        migrations.AlterModelOptions(
            name='passport',
            options={'verbose_name': 'Паспорт', 'verbose_name_plural': 'Паспорта'},
        ),
        migrations.AlterModelOptions(
            name='price',
            options={'verbose_name': 'Цена', 'verbose_name_plural': 'Цены'},
        ),
        migrations.AlterField(
            model_name='contract',
            name='date_of_contract',
            field=models.DateField(default=datetime.datetime(2024, 7, 2, 20, 12, 9, 828352), verbose_name='Дата'),
        ),
        migrations.AlterField(
            model_name='objectdevice',
            name='date_of_commissioning',
            field=models.DateField(blank=True, default=datetime.datetime(2024, 7, 2, 20, 12, 9, 829353), null=True, verbose_name='Дата ввода в эксплуатацию'),
        ),
        migrations.AlterField(
            model_name='objectdevice',
            name='date_of_manufacture',
            field=models.DateField(blank=True, default=datetime.datetime(2024, 7, 2, 20, 12, 9, 829353), null=True, verbose_name='Дата изготовления'),
        ),
        migrations.AlterField(
            model_name='objectdevice',
            name='kind',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='gas.devicekind', verbose_name='Тип'),
        ),
        migrations.AlterField(
            model_name='objectdevice',
            name='manufacter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='gas.devicemanufacter', verbose_name='Производитель'),
        ),
        migrations.AlterField(
            model_name='objectdevice',
            name='model',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='gas.devicemodel', verbose_name='Модель'),
        ),
        migrations.AlterField(
            model_name='objectdevice',
            name='modification',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='gas.devicemodification', verbose_name='Модификация'),
        ),
        migrations.AlterField(
            model_name='objectdevice',
            name='sn',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Серийный номер'),
        ),
    ]