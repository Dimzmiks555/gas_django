import datetime
import re
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from gas.models import Act, Client, Master, Object


@override_settings(ROOT_URLCONF='app.urls')
class ActPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='list-manager')
        cls.master = Master.objects.create(lastname='Тестов', firstname='Иван', middlename='Иванович')
        cls.obj = Object.objects.create(city='Тестовый', street='Примерная', house='10')
        objects = [cls.obj] + [Object.objects.create(city='Тестовый') for _ in range(54)]
        Client.objects.bulk_create([Client(object=obj, lastname='Клиент', firstname='Иван', middlename='Иванович') for obj in objects])
        Act.objects.bulk_create([Act(object=cls.obj, act_number=str(i), total=100, date_of_act=datetime.date(2026, 10, 15)) for i in range(55)])
        cls.posted = Act.objects.create(object=cls.obj, act_number='Проведённый', total=200, master=cls.master, is_posted=True, to_edit=True, date_of_act='2026-10-16')

    def setUp(self):
        self.client.force_login(self.user)

    def test_both_lists_have_50_items_and_preserve_filters(self):
        for path, query, total in [('/objects/', 'last_name=Клиент', 55), ('/acts/', 'address=Тестовый', 56)]:
            with self.subTest(path=path):
                first = self.client.get(path + '?' + query)
                self.assertEqual(first.status_code, 200)
                self.assertEqual(len(first.context['object_list']), 50)
                self.assertEqual(first.context['total'], total)
                self.assertContains(first, 'page=2')
                second = self.client.get(path + '?' + query + '&page=2')
                self.assertEqual(len(second.context['object_list']), total - 50)
                self.assertFalse(set(first.context['object_list']) & set(second.context['object_list']))
                self.assertIn(query.split('=')[0], second.context['filter_query'])

    def test_act_filters_combine_and_dates_are_inclusive(self):
        response = self.client.get('/acts/', {'number': 'Провед', 'object_id': self.obj.pk, 'address': 'Тестовый Примерная', 'master': self.master.pk, 'status': 'posted', 'to_edit': 'on', 'date_from': '2026-10-16', 'date_to': '2026-10-16'})
        self.assertEqual(list(response.context['object_list']), [self.posted])
        response = self.client.get('/acts/', {'master': 'none', 'status': 'unposted'})
        self.assertEqual(response.context['total'], 55)

    def test_invalid_filters_render_errors(self):
        for query in ({'object_id': 'bad'}, {'master': 'bad'}, {'date_from': '2026-10-20', 'date_to': '2026-10-01'}, {'date_from': 'bad'}):
            response = self.client.get('/acts/', query)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context['filter_form'].errors)
            self.assertEqual(response.context['total'], 0)

    def test_standalone_post_and_lock(self):
        act = Act.objects.filter(is_posted=False).first()
        act.master = self.master
        act.save()
        path = f'/acts/{act.pk}/'
        page = self.client.get(path)
        self.assertContains(page, 'К списку актов')
        self.assertContains(page, f'action="{path}"')
        token = re.search(r'name="_submission_token" value="([^"]+)"', page.content.decode())[1]
        response = self.client.post(path, {'_submission_token': token, 'revision': act.revision, 'action': 'post', 'date_of_act': str(act.date_of_act), 'master': self.master.pk})
        self.assertRedirects(response, path + '?saved=1')
        act.refresh_from_db()
        self.assertTrue(act.is_posted)
        page = self.client.get(path)
        self.assertContains(page, 'Пометить на редактирование')
        self.assertNotContains(page, 'name="date_of_act"')

    def test_lists_and_detail_require_login(self):
        self.client.logout()
        for path in ('/acts/', '/objects/', f'/acts/{self.posted.pk}/'):
            self.assertEqual(self.client.get(path).status_code, 302)
