# Generated by Django 5.0.6 on 2024-07-04 15:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gas', '0015_alter_act_options_remove_act_summ_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='act',
            name='date_of_act',
            field=models.DateField(default=datetime.datetime(2024, 7, 4, 18, 22, 8, 180416), verbose_name='Дата'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='date_of_contract',
            field=models.DateField(default=datetime.datetime(2024, 7, 4, 18, 22, 8, 180416), verbose_name='Дата'),
        ),
    ]
