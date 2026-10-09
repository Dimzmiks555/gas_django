"""Container settings. Persistent application data lives outside the image."""
from .settings import *  # noqa: F403
from django.core.exceptions import ImproperlyConfigured

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if len(SECRET_KEY) < 50:
    raise ImproperlyConfigured("Set DJANGO_SECRET_KEY to a random value of at least 50 characters")
DEBUG = False
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]
CSRF_TRUSTED_ORIGINS = [h.strip() for h in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if h.strip()]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "/data/db.sqlite3", "OPTIONS": {"timeout": 20}}}
GENERATED_DOCS_ROOT = Path("/data/generated_docs")
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
MIDDLEWARE.insert(MIDDLEWARE.index("django.contrib.auth.middleware.AuthenticationMiddleware") + 1,
                  "django.contrib.auth.middleware.LoginRequiredMiddleware")
ROOT_URLCONF = "app.urls_docker"
# Enable only behind the trusted Cloudflare connector; the host port stays loopback-only.
if os.environ.get("DJANGO_BEHIND_HTTPS_PROXY", "0") == "1":
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
