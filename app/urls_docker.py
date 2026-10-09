from django.contrib.auth.decorators import login_not_required
from django.db import connection
from django.http import JsonResponse
from django.urls import path
from .urls import urlpatterns as application_patterns


@login_not_required
def health(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    return JsonResponse({"status": "ok"})


# Legacy import writes to the database through an unprotected GET endpoint.
urlpatterns = [path("healthz/", health)] + [
    route for route in application_patterns if str(route.pattern) != "import/"
]
