import io
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from openpyxl import load_workbook
from .models import Object, Act, Contract


@override_settings(ROOT_URLCONF='app.urls')
class ExportTests(TestCase):
    def test_login_required(self):
        for url in ['/export/', '/export/acts/', '/export/objects/']:
            self.assertEqual(self.client.get(url).status_code, 302)

    def test_archives_contain_all_rows_current_documents_and_missing_status(self):
        self.client.force_login(get_user_model().objects.create_user('export-user'))
        obj = Object.objects.create(city='Тест', comment='=1+1')
        act = Act.objects.create(object=obj, act_number='1', total=172, document_file='revision.docx')
        Act.objects.create(object=obj, act_number='2', total=0)
        contract = Contract.objects.create(object=obj, contract_number='1', summ=172, status='active')
        with TemporaryDirectory() as directory, override_settings(GENERATED_DOCS_ROOT=Path(directory)):
            Path(directory, 'revision.docx').write_bytes(b'current act')
            Path(directory, f'contract-{contract.pk}.docx').write_bytes(b'contract')
            for kind in ['acts', 'objects']:
                response = self.client.get(f'/export/{kind}/')
                self.assertEqual(response.status_code, 200)
                data = b''.join(response.streaming_content)
                response.close()
                with ZipFile(io.BytesIO(data)) as archive:
                    workbook = load_workbook(io.BytesIO(archive.read('Реестр.xlsx')))
                    ws = workbook['Акты']
                    self.assertEqual(ws.max_row, 3)
                    rows = list(ws.values)[1:]
                    present = next(row for row in rows if row[0] == str(act.pk))
                    self.assertEqual(archive.read(present[9]), b'current act')
                    self.assertIn('Файл отсутствует', [row[10] for row in rows])
                    self.assertEqual(present[8], 172)
                    if kind == 'objects':
                        self.assertEqual(workbook['Объекты']['I2'].value, '=1+1')
                        self.assertEqual(workbook['Объекты']['I2'].data_type, 's')
                        self.assertEqual(archive.read(workbook['Договоры']['G2'].value), b'contract')
                    else:
                        self.assertEqual(workbook.sheetnames, ['Акты'])
                    workbook.close()
            self.assertContains(self.client.get('/export/'), 'Экспорт всех актов')
            self.assertEqual(self.client.get('/export/invalid/').status_code, 404)
