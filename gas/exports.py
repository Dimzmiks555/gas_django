"""Read-only XLSX and saved-document exports."""
from pathlib import Path
from tempfile import TemporaryFile
from zipfile import ZipFile, ZIP_DEFLATED

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import render
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from .act_documents import document_path
from .models import Act, Contract, Object, Client, ObjectDevice


@login_required
def export_page(request):
    return render(request, 'app/export.html')


def sheet(workbook, name, headers, rows):
    ws = workbook.create_sheet(name)
    ws.append(headers)
    for row in rows:
        ws.append(row)
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions
    for cell in ws[1]:
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill('solid', fgColor='245A70')
    for column in ws.columns:
        ws.column_dimensions[column[0].column_letter].width = min(60, max(16, max(len(str(c.value or '')) for c in column) + 2))
        for cell in column:
            cell.alignment = Alignment(vertical='top', wrap_text=True)
            if isinstance(cell.value, str):
                # User data must remain text, including strings starting with '='.
                cell.data_type = 's'
            elif cell.is_date:
                cell.number_format = 'dd.mm.yyyy'
    return ws


def add_document(archive, path, destination):
    root = Path(settings.GENERATED_DOCS_ROOT).resolve()
    path = Path(path).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        return '', 'Файл отсутствует'
    archive.write(path, destination)
    return destination, 'Включён'


def build_export(kind):
    output = TemporaryFile()
    workbook = Workbook()
    workbook.remove(workbook.active)
    try:
        with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
            act_rows = []
            for act in Act.objects.select_related('object', 'master').order_by('object_id', 'date_of_act', 'pk').iterator():
                folder = f'Документы/Объект_{act.object_id or "без_объекта"}' if kind == 'objects' else 'Акты'
                filename, state = add_document(archive, document_path(act), f'{folder}/Акт_{act.pk}.docx')
                act_rows.append([str(act.pk), act.act_number, act.object_id, act.object.get_full_address() if act.object else '', act.date_of_act, str(act.master) if act.master else '', 'Проведён' if act.is_posted else 'Не проведён', act.to_edit, act.total, filename, state])
            sheet(workbook, 'Акты', ['ID акта', 'Номер', 'Объект', 'Адрес', 'Дата', 'Мастер', 'Статус', 'На редактирование', 'Сумма, руб.', 'Файл в архиве', 'Документ'], act_rows)
            if kind == 'objects':
                sheet(workbook, 'Объекты', ['Объект', 'Тип обращения', 'Тип домовладения', 'Область', 'Район', 'Адрес', 'Индекс', 'Дата пуска газа', 'Примечание', 'На редактирование'], (
                    [o.pk, o.get_visit_type_display() or 'Не указано', o.type_of_building, o.region, o.area, o.get_full_address(), o.postcode, o.gas_date, o.comment, bool(o.to_edit)] for o in Object.objects.order_by('pk').iterator()))
                sheet(workbook, 'Клиенты', ['ID клиента', 'Объект', 'Фамилия', 'Имя', 'Отчество', 'Роль', 'Ответственный', 'Телефон 1', 'Телефон 2', 'Телефон 3'], (
                    [c.pk, c.object_id, c.lastname, c.firstname, c.middlename, c.role, c.is_main, c.phone_number_1, c.phone_number_2, c.phone_number_3] for c in Client.objects.order_by('object_id', 'pk').iterator()))
                sheet(workbook, 'Оборудование', ['ID оборудования', 'Объект', 'Категория', 'Тип', 'Модификация', 'Производитель', 'Модель', 'Серийный номер', 'Дата изготовления', 'Дата ввода', 'В договоре'], (
                    [d.pk, d.object_id, str(d.type), str(d.kind or ''), str(d.modification or ''), str(d.manufacter or ''), str(d.model or ''), d.sn, d.date_of_manufacture, d.date_of_commissioning, d.words_in_contract] for d in ObjectDevice.objects.select_related('type', 'kind', 'modification', 'manufacter', 'model').order_by('object_id', 'pk').iterator()))
                contracts = []
                for c in Contract.objects.order_by('object_id', 'date_of_contract', 'pk').iterator():
                    path = settings.GENERATED_DOCS_ROOT / f'contract-{c.pk}.docx'
                    if not path.exists():
                        date = c.date_of_contract
                        path = settings.GENERATED_DOCS_ROOT / f'Договор № {c.contract_number} от {date.day}.{date.month}.{date.year}.docx'
                    filename, state = add_document(archive, path, f'Документы/Объект_{c.object_id or "без_объекта"}/Договор_{c.pk}.docx')
                    contracts.append([str(c.pk), c.contract_number, c.object_id, c.date_of_contract, c.status, c.summ, filename, state])
                sheet(workbook, 'Договоры', ['ID договора', 'Номер', 'Объект', 'Дата', 'Статус', 'Сумма, руб.', 'Файл в архиве', 'Документ'], contracts)
            with TemporaryFile() as excel:
                workbook.save(excel)
                excel.seek(0)
                with archive.open('Реестр.xlsx', 'w') as target:
                    from shutil import copyfileobj
                    copyfileobj(excel, target)
        output.seek(0)
        return output
    except Exception:
        output.close()
        raise
    finally:
        workbook.close()


@login_required
def export_download(request, kind):
    if kind not in ('acts', 'objects'):
        raise Http404
    return FileResponse(build_export(kind), as_attachment=True,
                        filename=f'{kind}-{timezone.localdate().isoformat()}.zip', content_type='application/zip')
