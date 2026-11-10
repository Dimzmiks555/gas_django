from decimal import Decimal
from types import SimpleNamespace
from django.test import TestCase
from gas.models import DeviceType, Price
from gas.utils import get_pricelist_array


class SeparateSafetyDevicePricesTests(TestCase):
    def setUp(self):
        self.sensor = DeviceType.objects.create(name='Сигнализатор')
        self.valve = DeviceType.objects.create(name='Электромагнитный клапан')
        names = [
            'Техническое обслуживание котла',
            'Техническое обслуживание плиты газовой',
            'Техническое обслуживание духового шкафа',
            'Техническое обслуживание внутриквартирной газовой разводки',
            'Техническое обслуживание газовой колонки',
            'Инструктаж потребителя газа',
        ]
        for name in names:
            Price.objects.create(name=name, price=0)
        Price.objects.create(type=self.sensor, name='Техническое обслуживание сигнализатора загазованности (кроме проверки контрольными смесями)', price=301)
        Price.objects.create(type=self.valve, name='Техническое обслуживание электромагнитного клапана (при наличии)', price=350)

    def calculate(self, types):
        devices = [SimpleNamespace(type=t) for t in types]
        obj = SimpleNamespace(objectdevice_set=SimpleNamespace(all=lambda: devices))
        return get_pricelist_array(obj)

    def test_two_sensors_and_one_valve_have_independent_prices_and_totals(self):
        prices = self.calculate([self.sensor, self.valve, self.sensor])
        self.assertEqual((prices['18']['amount'], prices['18']['price'], prices['18']['total']), (2, Decimal('301'), Decimal('602')))
        self.assertEqual((prices['21']['amount'], prices['21']['price'], prices['21']['total']), (1, Decimal('350'), Decimal('350')))
        self.assertEqual(sum(p['total'] for p in prices.values()), Decimal('952'))

    def test_valve_does_not_increment_sensors(self):
        prices = self.calculate([self.valve])
        self.assertEqual(prices['18']['amount'], 0)
        self.assertEqual(prices['21']['amount'], 1)

    def test_no_safety_devices_have_zero_totals(self):
        prices = self.calculate([])
        self.assertEqual(prices['18']['total'], 0)
        self.assertEqual(prices['21']['total'], 0)

    def test_act_template_renders_separate_rows(self):
        from io import BytesIO
        from zipfile import ZipFile
        from xml.etree import ElementTree
        from django.conf import settings
        from docxtpl import DocxTemplate
        prices = self.calculate([self.sensor, self.sensor, self.valve])
        doc = DocxTemplate(settings.BASE_DIR / 'docx/act.docx')
        doc.render({'prices': prices, 'summ': 952})
        output = BytesIO()
        doc.save(output)
        with ZipFile(output) as archive:
            root = ElementTree.fromstring(archive.read('word/document.xml'))
        text = ''.join(root.itertext())
        self.assertIn('602', text)
        self.assertIn('350', text)
        self.assertIn('Техническое обслуживание электромагнитного клапана (при наличии)', text)
        self.assertIn('с учетом НДС', text)
        self.assertNotIn('{{', text)

    def test_act_lists_instruction_without_water_heater_row(self):
        from io import BytesIO
        from django.conf import settings
        from docxtpl import DocxTemplate
        from docx import Document
        heater = DeviceType.objects.create(name='Колонка')
        Price.objects.filter(name='Техническое обслуживание газовой колонки').update(type=heater, price=1065)
        Price.objects.filter(name='Инструктаж потребителя газа').update(price=172)
        prices = self.calculate([heater])
        total = sum(p['total'] for p in prices.values())
        self.assertEqual(total, Decimal('1237'))
        doc = DocxTemplate(settings.BASE_DIR / 'docx/act.docx')
        doc.render({'prices': prices, 'summ': total})
        output = BytesIO()
        doc.save(output)
        output.seek(0)
        rows = [[cell.text.strip() for cell in row.cells] for row in Document(output).tables[0].rows]
        self.assertFalse(any('Техническое обслуживание газовой колонки' in row[0] for row in rows))
        for name, price in [('Инструктаж потребителя газа', '172')]:
            with self.subTest(service=name):
                matches = [r for r in rows if r[0] == name]
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0][1], '1')
                self.assertIn(price, matches[0][2])
                self.assertIn(price, matches[0][3])
        self.assertIn('1237', rows[-1][0])
