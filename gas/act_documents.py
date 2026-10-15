"""Update act metadata without recalculating historical prices or replacing the template."""
import io
import re
import uuid
from zipfile import ZipFile
from lxml import etree
from django.conf import settings
from django.core.exceptions import ValidationError
from .models import Act
from .utils import save_document, transform_date_month

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def document_path(act):
    if act.document_file:
        return settings.GENERATED_DOCS_ROOT / act.document_file
    current = settings.GENERATED_DOCS_ROOT / f'act-{act.pk}.docx'
    if current.exists():
        return current
    date = act.date_of_act
    return settings.GENERATED_DOCS_ROOT / f'Акт № {act.act_number} от {date.day}.{date.month}.{date.year}.docx'


def initials(master):
    if master is None:
        return '________________'
    return f'{master.lastname} {master.firstname[:1]}. {master.middlename[:1]}.'


def replace_span(nodes, start, end, replacement):
    offset, inserted = 0, False
    for node in nodes:
        text = node.text or ''
        finish = offset + len(text)
        if finish > start and offset < end:
            prefix = text[:max(0, start - offset)]
            suffix = text[max(0, end - offset):]
            node.text = prefix + (replacement if not inserted else '') + suffix
            node.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            inserted = True
        offset = finish


def prepare_revision(act, date, master):
    path = document_path(act)
    if not path.exists():
        raise ValidationError('Файл акта не найден. Перед изменением реквизитов администратору нужно восстановить документ.')
    if path.name.startswith('Акт №') and Act.objects.filter(
            act_number=act.act_number, date_of_act=act.date_of_act).exclude(object_id=act.object_id).exists():
        raise ValidationError('Этот старый файл связан с несколькими объектами. Администратору нужно сначала проверить документ.')
    output = io.BytesIO()
    with ZipFile(path) as source, ZipFile(output, 'w') as destination:
        root = etree.fromstring(source.read('word/document.xml'))
        counts = [0, 0, 0]
        month = transform_date_month(date.strftime('%d.%m.%Y'), '.')
        replacements = [
            (re.compile(r'^№\s*.+?\s+от\s+«\d+»\s+\S+\s+\d{4}\s*г\.'),
             f'№ {act.act_number} от «{date.day}» {month} {date.year} г.'),
            (re.compile(r'(?<=газового оборудования ).*?(?=, с другой стороны)'), initials(master)),
            (re.compile(r'(?<=________________/).*?(?=/)'), initials(master)),
        ]
        for paragraph in root.iter(W + 'p'):
            nodes = list(paragraph.iter(W + 't'))
            text = ''.join(n.text or '' for n in nodes)
            for index, (pattern, replacement) in enumerate(replacements):
                match = pattern.search(text)
                if match:
                    # An old document can contain an empty master run. Replace
                    # the surrounding signature/phrase in that case as well.
                    start, end = match.span()
                    if start == end:
                        start -= 1
                        replacement = text[start] + replacement
                    replace_span(nodes, start, end, replacement)
                    counts[index] += 1
        if counts != [1, 1, 1]:
            raise ValidationError('Не удалось однозначно распознать реквизиты старого акта. Требуется проверка документа администратором.')
        for entry in source.infolist():
            data = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True) if entry.filename == 'word/document.xml' else source.read(entry.filename)
            destination.writestr(entry, data)
    return output.getvalue()


def store_revision(act, content):
    class DocumentBytes:
        def save(self, stream):
            stream.write(content)
    identifier = f'{act.pk}-{uuid.uuid4().hex}'
    save_document(DocumentBytes(), 'act', identifier)
    # Retain the previous file: a failed DB transaction must not replace it.
    act.document_file = f'act-{identifier}.docx'
