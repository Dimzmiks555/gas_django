# Generated by Django 5.0.4 on 2024-07-02 20:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gas', '0010_alter_contract_date_of_contract_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='date_of_contract',
            field=models.DateField(default=datetime.datetime(2024, 7, 2, 23, 22, 28, 504658), verbose_name='Дата'),
        ),
        migrations.AlterField(
            model_name='objectdevice',
            name='date_of_commissioning',
            field=models.DateField(blank=True, default=datetime.datetime(2024, 7, 2, 23, 22, 28, 505659), null=True, verbose_name='Дата ввода в эксплуатацию'),
        ),
        migrations.AlterField(
            model_name='objectdevice',
            name='date_of_manufacture',
            field=models.DateField(blank=True, default=datetime.datetime(2024, 7, 2, 23, 22, 28, 505659), null=True, verbose_name='Дата изготовления'),
        ),
        migrations.AlterField(
            model_name='passport',
            name='getted_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата выдачи'),
        ),
    ]
