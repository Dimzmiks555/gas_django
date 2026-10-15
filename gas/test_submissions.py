import re
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.test import Client as TestClient, TestCase, TransactionTestCase, override_settings
from django.db import connections
from django.urls import path
from gas.models import DeviceType


def form_view(request):
    if request.method == 'POST':
        DeviceType.objects.create(name=request.POST.get('name', 'example'))
        if request.POST.get('fail'):
            raise ValueError('document failed')
        if not request.POST.get('invalid'):
            return HttpResponseRedirect('/done/')
    return HttpResponse('<html><body><form method="post"><input name="name"></form></body></html>')


urlpatterns = [path('save/', form_view), path('other/', form_view)]


@override_settings(ROOT_URLCONF=__name__)
class SubmissionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='forms')
        self.client.force_login(self.user)

    def token(self, client=None):
        response = (client or self.client).get('/save/')
        match = re.search(r'name="_submission_token" value="([^"]+)"', response.content.decode())
        self.assertIsNotNone(match, 'POST forms must have a server-issued token')
        return match[1]

    def test_repeat_only_saves_once(self):
        data = {'_submission_token': self.token(), 'name': 'one'}
        first = self.client.post('/save/', data)
        second = self.client.post('/save/', data)
        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.url, first.url)
        self.assertEqual(DeviceType.objects.count(), 1)

    def test_new_form_is_an_independent_operation(self):
        for _ in range(2):
            self.assertEqual(self.client.post('/save/', {'_submission_token': self.token()}).status_code, 302)
        self.assertEqual(DeviceType.objects.count(), 2)

    def test_missing_token_cannot_write(self):
        self.assertEqual(self.client.post('/save/', {'name': 'one'}).status_code, 409)
        self.assertEqual(DeviceType.objects.count(), 0)

    def test_error_rolls_back_and_allows_retry(self):
        token = self.token()
        with self.assertRaisesMessage(ValueError, 'document failed'):
            self.client.post('/save/', {'_submission_token': token, 'fail': '1'})
        self.assertEqual(DeviceType.objects.count(), 0)
        self.assertEqual(self.client.post('/save/', {'_submission_token': token}).status_code, 302)
        self.assertEqual(DeviceType.objects.count(), 1)

    def test_validation_error_does_not_consume_token(self):
        token = self.token()
        self.assertEqual(self.client.post('/save/', {'_submission_token': token, 'invalid': '1'}).status_code, 200)
        self.assertEqual(DeviceType.objects.count(), 0)
        self.assertEqual(self.client.post('/save/', {'_submission_token': token}).status_code, 302)

    def test_token_cannot_be_used_for_another_action_or_user(self):
        token = self.token()
        self.assertEqual(self.client.post('/other/', {'_submission_token': token}).status_code, 409)
        other = get_user_model().objects.create_user(username='other')
        self.client.force_login(other)
        self.assertEqual(self.client.post('/save/', {'_submission_token': token}).status_code, 409)
        self.assertEqual(DeviceType.objects.count(), 0)

    def test_changed_payload_after_success_is_rejected(self):
        token = self.token()
        self.client.post('/save/', {'_submission_token': token, 'name': 'one'})
        self.assertEqual(self.client.post('/save/', {'_submission_token': token, 'name': 'two'}).status_code, 409)
        self.assertEqual(DeviceType.objects.count(), 1)

    @override_settings(ROOT_URLCONF='app.urls')
    def test_admin_save_replays_and_invalid_form_can_be_corrected(self):
        self.user.is_staff = self.user.is_superuser = True
        self.user.save()
        url = '/admin/gas/devicetype/add/'
        page = self.client.get(url).content.decode()
        token = re.search(r'name="_submission_token" value="([^"]+)"', page)[1]
        self.assertIn('form-submit.js', page)
        self.assertEqual(self.client.post(url, {'_submission_token': token, 'name': ''}).status_code, 200)
        data = {'_submission_token': token, 'name': 'admin test', '_save': 'Save'}
        self.assertEqual(self.client.post(url, data).status_code, 302)
        self.assertEqual(self.client.post(url, data).status_code, 302)
        self.assertEqual(DeviceType.objects.count(), 1)

    def test_csrf_is_still_required(self):
        client = TestClient(enforce_csrf_checks=True)
        client.force_login(self.user)
        token = self.token(client)
        self.assertEqual(client.post('/save/', {'_submission_token': token}).status_code, 403)
        self.assertEqual(DeviceType.objects.count(), 0)


@override_settings(ROOT_URLCONF=__name__)
class ConcurrentSubmissionTests(TransactionTestCase):
    def test_concurrent_posts_only_commit_once(self):
        user = get_user_model().objects.create_user(username='concurrent')
        clients = [TestClient(), TestClient()]
        for client in clients:
            client.force_login(user)
        page = clients[0].get('/save/').content.decode()
        token = re.search(r'name="_submission_token" value="([^"]+)"', page)[1]
        barrier = threading.Barrier(2)

        def submit(client):
            try:
                barrier.wait(timeout=5)
                return client.post('/save/', {'_submission_token': token}).status_code
            finally:
                connections.close_all()

        original = DeviceType.objects.create

        def slow_save(**kwargs):
            time.sleep(0.1)
            return original(**kwargs)

        with patch.object(DeviceType.objects, 'create', side_effect=slow_save):
            with ThreadPoolExecutor(max_workers=2) as executor:
                statuses = list(executor.map(submit, clients))
        self.assertIn(302, statuses)
        self.assertTrue(all(status in (302, 503) for status in statuses), statuses)
        self.assertEqual(clients[0].post('/save/', {'_submission_token': token}).status_code, 302)
        self.assertEqual(DeviceType.objects.count(), 1)


class DocumentSubmissionTests(TestCase):
    @override_settings(ROOT_URLCONF='app.urls')
    def test_contract_retry_and_unique_document_names(self):
        from gas.models import Client, Contract, Object, Passport
        self.client.force_login(get_user_model().objects.create_user(username='contract-test'))
        obj = Object.objects.create()
        Passport.objects.create(object=obj, getted_date='2020-01-01')
        Client.objects.create(object=obj, firstname='Test', lastname='Test', middlename='Test')
        url = f'/objects/{obj.pk}/contract/create'
        prices = {str(i): {'name': 'Test', 'amount': 0, 'price': 0, 'total': 0} for i in range(14, 22)}
        with tempfile.TemporaryDirectory() as directory, override_settings(GENERATED_DOCS_ROOT=Path(directory)):
            with patch('gas.views.get_pricelist_array', return_value=prices), patch('builtins.print'):
                for _ in range(2):
                    page = self.client.get(url).content.decode()
                    token = re.search(r'name="_submission_token" value="([^"]+)"', page)[1]
                    data = {'_submission_token': token, 'contract_number': 'test', 'date_day': '3',
                            'date_month': '7', 'date_year': '2026'}
                    self.assertEqual(self.client.post(url, data).status_code, 302)
                    self.assertEqual(self.client.post(url, data).status_code, 302)
                self.assertEqual(Contract.objects.count(), 2)
                self.assertEqual(Contract.objects.filter(status='active').count(), 1)
                self.assertEqual(len(list(Path(directory).glob('contract-*.docx'))), 2)
                download_url = f'/download/contract/{obj.pk}/'
                response = self.client.get(download_url)
                self.assertEqual(response.status_code, 200)
                response.close()
                active = Contract.objects.get(status='active')
                (Path(directory) / f'contract-{active.pk}.docx').rename(Path(directory) / 'Договор № test от 3.7.2026.docx')
                response = self.client.get(download_url)
                self.assertEqual(response.status_code, 200)
                response.close()

    @override_settings(ROOT_URLCONF='app.urls')
    def test_real_act_retry_files_and_legacy_download(self):
        from gas.models import Act, Client, Contract, Master, Object, Passport
        user = get_user_model().objects.create_user(username='act-test')
        self.client.force_login(user)
        obj = Object.objects.create()
        Passport.objects.create(object=obj, getted_date='2020-01-01')
        Client.objects.create(object=obj, firstname='Test', lastname='Test', middlename='Test')
        master = Master.objects.create(firstname='Test', lastname='Test', middlename='Test')
        Contract.objects.create(object=obj, contract_number='test', status='active', summ=0)
        url = f'/objects/{obj.pk}/act/create_from_contract'
        with tempfile.TemporaryDirectory() as directory, override_settings(GENERATED_DOCS_ROOT=Path(directory)):
            prices = {str(i): {'name': 'Test', 'amount': 0, 'price': 0, 'total': 0} for i in range(14, 22)}
            with patch('gas.views.get_pricelist_array', return_value=prices):
                page = self.client.get(url).content.decode()
                token = re.search(r'name="_submission_token" value="([^"]+)"', page)[1]
                data = {'_submission_token': token, 'act_number': '1713', 'date_day': '3',
                        'date_month': '7', 'date_year': '2026', 'master': master.pk}
                # A failed document generation must not leave a phantom act.
                with patch('gas.views.generate_act', side_effect=OSError('disk full')):
                    with self.assertRaises(OSError):
                        self.client.post(url, data)
                self.assertEqual(Act.objects.count(), 0)
                self.assertEqual(self.client.post(url, data).status_code, 302)
                self.assertEqual(self.client.post(url, data).status_code, 302)
            act = Act.objects.get()
            document = Path(directory) / f'act-{act.pk}.docx'
            self.assertTrue(document.exists())
            self.assertEqual(len(list(Path(directory).iterdir())), 1)
            download_url = f'/download/act/{act.pk}/'
            self.assertEqual(self.client.get(download_url).status_code, 200)
            document.rename(Path(directory) / 'Акт № 1713 от 3.7.2026.docx')
            self.assertEqual(self.client.get(download_url).status_code, 200)

    def test_failed_file_write_leaves_no_partial_file(self):
        from gas.utils import save_document

        class BrokenDocument:
            def save(self, stream):
                stream.write(b'partial')
                raise OSError('disk full')

        with tempfile.TemporaryDirectory() as directory, override_settings(GENERATED_DOCS_ROOT=Path(directory)):
            with self.assertRaises(OSError):
                save_document(BrokenDocument(), 'act', 'test')
            self.assertEqual(list(Path(directory).iterdir()), [])
