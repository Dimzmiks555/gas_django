import re
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from gas.models import Object


@override_settings(ROOT_URLCONF='app.urls')
class ObjectVisitTypeTests(TestCase):
    def setUp(self):
        self.client.force_login(get_user_model().objects.create_user(username='visit-manager'))
        self.obj = Object.objects.create(comment='Сохранить примечание')
        self.path = f'/objects/{self.obj.pk}/visit-type/'

    def payload(self, value):
        html = self.client.get(f'/objects/{self.obj.pk}').content.decode()
        form = re.search(r'<form[^>]+action="' + re.escape(self.path) + r'"[^>]*>(.*?)</form>', html, re.S)[1]
        token = re.search(r'name="_submission_token" value="([^"]+)"', form)[1]
        return {'visit_type': value, '_submission_token': token}

    def test_choices_save_and_repeat_is_safe(self):
        self.assertEqual(self.obj.visit_type, '')
        for value in ['initial', 'renewal', 'new_owner', '']:
            data = self.payload(value)
            self.assertEqual(self.client.post(self.path, data).status_code, 302)
            self.assertEqual(self.client.post(self.path, data).status_code, 302)
            self.obj.refresh_from_db()
            self.assertEqual(self.obj.visit_type, value)
            self.assertEqual(self.obj.comment, 'Сохранить примечание')

    def test_invalid_value_is_not_saved(self):
        response = self.client.post(self.path, self.payload('invalid'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['visit_type_form'].errors)
        self.obj.refresh_from_db()
        self.assertEqual(self.obj.visit_type, '')

    def test_requires_post_and_login(self):
        self.assertEqual(self.client.get(self.path).status_code, 405)
        self.client.logout()
        self.assertEqual(self.client.post(self.path, {'visit_type': 'initial'}).status_code, 302)
