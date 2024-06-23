# Generated by Django 5.0.4 on 2024-06-23 09:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gas', '0010_remove_object_clients_client_object'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='object',
        ),
        migrations.AddField(
            model_name='client',
            name='object',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='gas.object', verbose_name='Объект'),
            preserve_default=False,
        ),
    ]