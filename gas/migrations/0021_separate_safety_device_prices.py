from django.db import migrations


OLD_NAME = 'Техническое обслуживание сигнализатора / э/м клапана'
NAMES = {
    'Сигнализатор': 'Техническое обслуживание сигнализатора загазованности (кроме проверки контрольными смесями)',
    'Электромагнитный клапан': 'Техническое обслуживание электромагнитного клапана (при наличии)',
}


def separate(apps, schema_editor):
    prices = apps.get_model('gas', 'Price').objects.using(schema_editor.connection.alias)
    for category, name in NAMES.items():
        prices.filter(type__name=category, name=OLD_NAME).update(name=name)


def combine(apps, schema_editor):
    prices = apps.get_model('gas', 'Price').objects.using(schema_editor.connection.alias)
    for category, name in NAMES.items():
        prices.filter(type__name=category, name=name).update(name=OLD_NAME)


class Migration(migrations.Migration):
    dependencies = [('gas', '0020_alter_act_date_of_act_alter_act_object_and_more')]
    operations = [migrations.RunPython(separate, combine)]
