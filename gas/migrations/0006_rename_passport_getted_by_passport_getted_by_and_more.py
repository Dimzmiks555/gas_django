# Generated by Django 5.0.4 on 2024-05-01 14:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gas', '0005_remove_client_phones_remove_object_clients_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='passport',
            old_name='passport_getted_by',
            new_name='getted_by',
        ),
        migrations.RenameField(
            model_name='passport',
            old_name='passport_getted_date',
            new_name='getted_date',
        ),
        migrations.RenameField(
            model_name='passport',
            old_name='passport_number',
            new_name='number',
        ),
        migrations.RenameField(
            model_name='passport',
            old_name='passport_serial',
            new_name='serial',
        ),
    ]