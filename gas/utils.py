from docxtpl import DocxTemplate
import datetime
from pathlib import Path
import uuid

BASE_DIR = Path(__file__).resolve().parent.parent

def generate_docx(data):

    uuid_number = uuid.uuid4()

    contract = DocxTemplate(BASE_DIR / "docx/contract.docx")
    contract.render(data)
    contract.save(BASE_DIR / f"generated_docs/Договор № {data['contract_number']}-OBJ{data['object_id']}-{data['date_day']}.{data['date_month']}.{data['date_year']}-{uuid_number}.docx")
    act = DocxTemplate(BASE_DIR / "docx/act.docx")
    act.render(data)
    act.save(BASE_DIR / f"generated_docs/Акт № {data['contract_number']}-OBJ{data['object_id']}-{data['date_day']}.{data['date_month']}.{data['date_year']}-{uuid_number}.docx")
    
def transform_date_month(date):
    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
           'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    day,month,year = date.split('.')
    return f'{months[int(month) - 1]}'

def get_full_address(data):

    if (data.room):
        data.type_of_building = 'кв.'
    else:
        data.type_of_building = ''

    data.type_of_city = data.type_of_city[:1].lower() + data.type_of_city[1:]

    string = f'{data.region} обл., {data.area} район, {data.type_of_city} {data.city}, {data.street_type} {data.street}, д. {data.house} {data.type_of_building} {data.room}' 
    return string
