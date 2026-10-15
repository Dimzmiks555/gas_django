import re
import tempfile
from pathlib import Path
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from gas.models import Act, Client, Contract, Master, Object, Passport

@override_settings(ROOT_URLCONF='app.urls')
class ActWorkflowTests(TestCase):
    def setUp(self):
        self.client.force_login(get_user_model().objects.create_user(username='manager'))
        self.obj = Object.objects.create(street_type='ул.', street='Тестовая')
        Passport.objects.create(object=self.obj, getted_date='2020-01-01')
        Client.objects.create(object=self.obj, firstname='Иван', lastname='Тестов', middlename='Иванович')
        Contract.objects.create(object=self.obj, status='active', contract_number='test', summ=100)
        self.master = Master.objects.create(firstname='Иван', lastname='Мастер', middlename='Иванович')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        override = override_settings(GENERATED_DOCS_ROOT=Path(self.tmp.name))
        override.enable()
        self.addCleanup(override.disable)
        prices = {str(i): {'name': 'Test', 'amount': 0, 'price': 0, 'total': 0} for i in range(14,22)}
        prices['14'].update(amount=1, price=123, total=123)
        self.prices = patch('gas.views.get_pricelist_array', return_value=prices)
        self.prices.start()
        self.addCleanup(self.prices.stop)

    def token(self, path):
        page = self.client.get(path).content.decode()
        # Logout is not protected; the first token belongs to the act form.
        return re.search(r'name="_submission_token" value="([^"]+)"',page)[1]

    def create_act(self, master=''):
        path = f'/objects/{self.obj.pk}/act/create_from_contract'
        response = self.client.post(path, {'_submission_token': self.token(path), 'act_number': '100',
            'date_day':'15','date_month':'10','date_year':'2026','master':master})
        self.assertEqual(response.status_code,302)
        return Act.objects.get()

    def edit(self, act, **data):
        path = f'/objects/{self.obj.pk}/acts/{act.pk}/'
        return self.client.post(path, {'_submission_token': self.token(path),
            'date_of_act':'2026-10-16', 'master':'', 'revision':act.revision, 'action':'save', **data})

    def test_create_without_master_is_unposted(self):
        act = self.create_act()
        self.assertIsNone(act.master_id)
        self.assertFalse(act.is_posted)

    def test_invalid_master_displays_creation_errors(self):
        path = f'/objects/{self.obj.pk}/act/create_from_contract'
        response = self.client.post(path, {'_submission_token': self.token(path), 'act_number': '100',
            'date_day': '15', 'date_month': '10', 'date_year': '2026', 'master': '99999'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['act_form'].is_bound)
        self.assertIn('master', response.context['act_form'].errors)
        self.assertFalse(Act.objects.exists())

    def test_post_requires_master_then_locks_editing(self):
        act = self.create_act()
        self.assertEqual(self.edit(act, action='post').status_code,200)
        act.refresh_from_db()
        self.assertFalse(act.is_posted)
        self.assertEqual(self.edit(act, action='post', master=self.master.pk).status_code,302)
        act.refresh_from_db()
        self.assertTrue(act.is_posted)
        self.assertEqual(self.edit(act, master='', date_of_act='2026-10-20').status_code,200)
        act.refresh_from_db()
        self.assertEqual(str(act.date_of_act),'2026-10-16')
        self.assertEqual(act.master_id,self.master.pk)

    def test_mark_does_not_unlock_posted_act(self):
        act = self.create_act(self.master.pk)
        self.edit(act, action='post', master=self.master.pk)
        act.refresh_from_db()
        self.assertEqual(self.edit(act, action='mark').status_code,302)
        act.refresh_from_db()
        self.assertTrue(act.to_edit)
        self.assertTrue(act.is_posted)

    def test_change_preserves_prices_and_updates_document(self):
        from zipfile import ZipFile
        from lxml import etree
        act = self.create_act()
        self.assertEqual(self.edit(act, master=self.master.pk).status_code,302)
        act.refresh_from_db()
        self.assertEqual(act.total,123)
        with ZipFile(Path(self.tmp.name)/act.document_file) as z:
            text=''.join(etree.fromstring(z.read('word/document.xml')).itertext())
        self.assertIn('«16» октября 2026',text)
        self.assertIn('Мастер И. И.',text)
        self.assertIn('123',text)
        self.assertNotIn('None',text)

    def test_stale_form_cannot_overwrite_changes(self):
        act = self.create_act()
        self.edit(act, master=self.master.pk)
        response=self.edit(act,date_of_act='2026-10-20')
        self.assertEqual(response.status_code,200)
        act.refresh_from_db()
        self.assertEqual(str(act.date_of_act),'2026-10-16')

    def test_object_scope_cannot_be_changed(self):
        act=self.create_act()
        other=Object.objects.create()
        self.assertEqual(self.client.get(f'/objects/{other.pk}/acts/{act.pk}/').status_code,404)

    def test_editor_can_be_embedded_only_on_same_site(self):
        act = self.create_act()
        response = self.client.get(f'/objects/{self.obj.pk}/acts/{act.pk}/')
        self.assertEqual(response.headers['X-Frame-Options'], 'SAMEORIGIN')
        self.assertContains(response, f'href="/download/act/{act.pk}/" target="_top"')

    def test_admin_can_correct_posted_act_and_document(self):
        act = self.create_act(self.master.pk)
        self.edit(act, action='post', master=self.master.pk)
        act.refresh_from_db()
        old_document = act.document_file
        admin = get_user_model().objects.create_superuser(username='administrator', password='test')
        self.client.force_login(admin)
        path = f'/admin/gas/act/{act.pk}/change/'
        response = self.client.post(path, {'_submission_token': self.token(path),
            'date_of_act': '2026-10-20', 'master': self.master.pk, 'is_posted': 'on', '_save': 'Сохранить'})
        self.assertEqual(response.status_code, 302)
        act.refresh_from_db()
        self.assertTrue(act.is_posted)
        self.assertEqual(str(act.date_of_act), '2026-10-20')
        self.assertNotEqual(act.document_file, old_document)
        self.assertTrue((Path(self.tmp.name) / old_document).exists())
