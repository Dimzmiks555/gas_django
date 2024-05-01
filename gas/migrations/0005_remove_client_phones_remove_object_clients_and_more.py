# Generated by Django 5.0.4 on 2024-05-01 13:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gas', '0004_alter_object_clients_alter_object_contracts_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='phones',
        ),
        migrations.RemoveField(
            model_name='object',
            name='clients',
        ),
        migrations.RemoveField(
            model_name='object',
            name='contracts',
        ),
        migrations.AddField(
            model_name='client',
            name='object',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gas.object'),
        ),
        migrations.AddField(
            model_name='contract',
            name='object',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gas.object'),
        ),
        migrations.AddField(
            model_name='phone',
            name='client',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='gas.client'),
            preserve_default=False,
        ),
    ]
