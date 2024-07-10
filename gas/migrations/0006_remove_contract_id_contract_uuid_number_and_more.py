# Generated by Django 5.0.4 on 2024-07-02 18:03

import datetime
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gas', '0005_alter_contract_contract_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contract',
            name='id',
        ),
        migrations.AddField(
            model_name='contract',
            name='uuid_number',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='contract',
            name='date_of_contract',
            field=models.DateField(default=datetime.datetime(2024, 7, 2, 21, 3, 57, 74154), verbose_name='Дата'),
        ),
        migrations.AlterField(
            model_name='objectdevice',
            name='date_of_commissioning',
            field=models.DateField(blank=True, default=datetime.datetime(2024, 7, 2, 21, 3, 57, 75155), null=True, verbose_name='Дата ввода в эксплуатацию'),
        ),
        migrations.AlterField(
            model_name='objectdevice',
            name='date_of_manufacture',
            field=models.DateField(blank=True, default=datetime.datetime(2024, 7, 2, 21, 3, 57, 75155), null=True, verbose_name='Дата изготовления'),
        ),
    ]