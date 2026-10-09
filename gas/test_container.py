from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import Resolver404, resolve


@override_settings(ROOT_URLCONF="app.urls_docker")
class ContainerAccessTests(TestCase):
    def setUp(self):
        middleware = list(settings.MIDDLEWARE)
        guard = "django.contrib.auth.middleware.LoginRequiredMiddleware"
        if guard not in middleware:
            middleware.insert(middleware.index("django.contrib.auth.middleware.AuthenticationMiddleware") + 1, guard)
        self.override = override_settings(MIDDLEWARE=middleware)
        self.override.enable()
        self.addCleanup(self.override.disable)

    def test_anonymous_access_is_blocked_before_document_lookup_or_mutation(self):
        for path in ["/objects/", "/objects/1/to_edit", "/download/contract/1/", "/download/act/invalid/"]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.url.startswith("/accounts/login/"))
        self.assertEqual(self.client.post("/objects/1/edit_comment", {"comment": "test"}).status_code, 302)

    def test_legacy_import_is_not_routed(self):
        with self.assertRaises(Resolver404):
            resolve("/import/")

    def test_health_is_available_without_login(self):
        self.assertEqual(self.client.get("/healthz/").json(), {"status": "ok"})

    def test_login_renders_with_static_asset_urls(self):
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/static/style.css')
