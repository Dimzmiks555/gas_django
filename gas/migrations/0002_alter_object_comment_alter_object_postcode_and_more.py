# Generated by Django 5.0.4 on 2024-05-01 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gas', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='object',
            name='comment',
            field=models.TextField(blank=True, verbose_name='Примечание'),
        ),
        migrations.AlterField(
            model_name='object',
            name='postcode',
            field=models.CharField(blank=True, max_length=50, verbose_name='Индекс'),
        ),
        migrations.AlterField(
            model_name='object',
            name='show_part',
            field=models.BooleanField(blank=True, verbose_name='Отображать часть дома/квартиру в документах'),
        ),
    ]