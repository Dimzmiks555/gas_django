from docxtpl import DocxTemplate
import datetime
from pathlib import Path
import uuid
from .models import Price 

BASE_DIR = Path(__file__).resolve().parent.parent

def generate_docx(data, uuid):

    uuid_number = uuid

    contract = DocxTemplate(BASE_DIR / "docx/contract.docx")
    contract.render(data)
    contract.save(BASE_DIR / f"generated_docs/Договор № {data['contract_number']}-OBJ{data['object_id']}-{data['date_day']}.{data['date_month']}.{data['date_year']}-{uuid_number}.docx")
    
    # act = DocxTemplate(BASE_DIR / "docx/act.docx")
    # act.render(data)
    # act.save(BASE_DIR / f"generated_docs/Акт № {data['contract_number']}-OBJ{data['object_id']}-{data['date_day']}.{data['date_month']}.{data['date_year']}-{uuid_number}.docx")
    
    one = DocxTemplate(BASE_DIR / "docx/1.docx")
    one.render(data)
    one.save(BASE_DIR / f"generated_docs/Приложение № 1 к договору № {data['contract_number']}-OBJ{data['object_id']}-{data['date_day']}.{data['date_month']}.{data['date_year']}-{uuid_number}.docx")
    
    two = DocxTemplate(BASE_DIR / "docx/2.docx")
    two.render(data)
    two.save(BASE_DIR / f"generated_docs/Приложение № 2 к договору № {data['contract_number']}-OBJ{data['object_id']}-{data['date_day']}.{data['date_month']}.{data['date_year']}-{uuid_number}.docx")
    
def generate_act(data, uuid):

    uuid_number = uuid

    act = DocxTemplate(BASE_DIR / "docx/act.docx")
    act.render(data)
    act.save(BASE_DIR / f"generated_docs/Акт № {data['act_number']}-OBJ{data['object_id']}-{data['date_day']}.{data['date_month']}.{data['date_year']}-{uuid_number}.docx")
   

def transform_date_month(date, separator):
    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
           'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    day,month,year = date.split(separator)
    return f'{months[int(month) - 1]}'

def get_full_address(data):

    if (data.room):
        data.type_of_building = 'кв.'
    else:
        data.type_of_building = ''

    data.type_of_city = data.type_of_city[:1].lower() + data.type_of_city[1:]

    string = f'{data.region} обл., {data.area} район, {data.type_of_city} {data.city}, {data.street_type} {data.street}, д. {data.house}, {data.type_of_building} {data.room}' 
    return string

def get_pricelist_array(object):

    list = {
        '14': {
            'name': 'Техническое обслуживание котла',
            'amount': 0,
            'price': 0,
            'total': 0
        },
        '15': {
            'name': 'Техническое обслуживание плиты газовой',
            'amount': 0,
            'price': 0,
            'total': 0
        },
        '16': {
            'name': 'Техническое обслуживание духового шкафа',
            'amount': 0,
            'price': 0,
            'total': 0
        },
        '17': {
            'name': 'Техническое обслуживание внутриквартирной газовой разводки',
            'amount': 1,
            'price': 0,
            'total': 0
        },
        '18': {
            'name': 'Техническое обслуживание сигнализатора',
            'amount': 0,
            'price': 0,
            'total': 0
        },
        '19': {
            'name': 'Техническое обслуживание газовой колонки',
            'amount': 0,
            'price': 0,
            'total': 0
        },
        '20': {
            'name': 'Инструктаж потребителя газа',
            'amount': 1,
            'price': 0,
            'total': 0
        },
    }

    for p in list:
        price = Price.objects.filter(name__contains=list[p]['name'])[0]
        list[p]['price'] = price.price
    
    for device in object.objectdevice_set.all():
        pr = Price.objects.filter(type=device.type)

        if len(pr) > 0:
            if 'Техническое обслуживание котла' in pr[0].name:
                list['14']['amount'] += 1
                list['14']['price'] = pr[0].price
            elif 'Техническое обслуживание плиты газовой' in pr[0].name:
                list['15']['amount'] += 1
                list['15']['price'] = pr[0].price
            elif 'Техническое обслуживание духового шкафа' in pr[0].name:
                list['16']['amount'] += 1
                list['16']['price'] = pr[0].price
            elif 'Техническое обслуживание сигнализатора' in pr[0].name:
                list['18']['amount'] += 1
                list['18']['price'] = pr[0].price
            elif 'Техническое обслуживание газовой колонки' in pr[0].name:
                list['19']['amount'] += 1
                list['19']['price'] = pr[0].price
    
    print(list)

    for p in list:
        list[p]['total'] = list[p]['amount'] * list[p]['price']

    return list