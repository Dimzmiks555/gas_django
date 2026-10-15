"""One committed write per server-issued form token, including admin forms."""
import hashlib
import json
import uuid
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from django.core import signing
from django.db import IntegrityError, OperationalError, transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.templatetags.static import static
from django.utils.cache import patch_cache_control
from django.utils.crypto import salted_hmac
from django.utils.html import format_html
from django.utils.deprecation import MiddlewareMixin

from .models import FormSubmission

FIELD = '_submission_token'
SALT = 'gas.form-submission'


def protected(path):
    return not (path.startswith('/accounts/') or path in ('/admin/login/', '/admin/logout/'))


def payload_digest(request):
    data = sorted((key, request.POST.getlist(key)) for key in request.POST
                  if key not in (FIELD, 'csrfmiddlewaretoken'))
    files = []
    for key in sorted(request.FILES):
        for upload in request.FILES.getlist(key):
            digest = hashlib.sha256()
            for chunk in upload.chunks():
                digest.update(chunk)
            upload.seek(0)
            files.append((key, upload.name, digest.hexdigest()))
    # Do not persist personal data or passwords in the submission registry.
    return salted_hmac(SALT, json.dumps([data, files]), algorithm='sha256').hexdigest()


class FormTokens(HTMLParser):
    def __init__(self, source, request):
        super().__init__(convert_charrefs=False)
        self.source, self.request = source, request
        self.lines = source.splitlines(keepends=True)
        self.insertions = []

    def source_offset(self):
        line, column = self.getpos()
        return sum(map(len, self.lines[:line - 1])) + column

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag != 'form' or attrs.get('method', 'get').lower() != 'post':
            return
        action = urlsplit(urljoin(self.request.build_absolute_uri(), attrs.get('action') or ''))
        if action.netloc != self.request.get_host() or not protected(action.path):
            return
        if not self.request.user.is_authenticated:
            return
        token = signing.dumps({'id': uuid.uuid4().hex, 'user': str(self.request.user.pk),
                               'path': action.path, 'query': action.query}, salt=SALT)
        self.insertions.append((self.source_offset() + len(self.get_starttag_text()),
                                str(format_html('<input type="hidden" name="{}" value="{}">', FIELD, token))))

    def handle_endtag(self, tag):
        if tag == 'body':
            self.insertions.append((self.source_offset(), str(format_html(
                '<script src="{}" defer></script>', static('form-submit.js')))))

    def output(self):
        result = self.source
        for offset, value in sorted(self.insertions, reverse=True):
            result = result[:offset] + value + result[offset:]
        return result


class SubmissionMiddleware(MiddlewareMixin):
    def process_view(self, request, view, args, kwargs):
        if request.method != 'POST' or not request.user.is_authenticated or not protected(request.path):
            return None
        try:
            token = signing.loads(request.POST.get(FIELD, ''), salt=SALT, max_age=7 * 86400)
            if (token['user'] != str(request.user.pk) or token['path'] != request.path
                    or token['query'] != request.META.get('QUERY_STRING', '')):
                raise signing.BadSignature()
            key = uuid.UUID(token['id']).hex
        except (signing.BadSignature, KeyError, ValueError, TypeError):
            return HttpResponse('Форма устарела. Откройте страницу заново и повторите отправку.', status=409)
        digest = payload_digest(request)
        try:
            with transaction.atomic():
                # INSERT is the first DB operation in this transaction. The unique
                # key arbitrates concurrent requests, including SQLite writers.
                try:
                    with transaction.atomic():
                        submission = FormSubmission.objects.create(key=key, digest=digest)
                except IntegrityError:
                    existing = FormSubmission.objects.get(pk=key)
                    if existing.digest != digest:
                        return HttpResponse('Эта форма уже сохранена. Для новых изменений откройте её заново.', status=409)
                    return HttpResponseRedirect(existing.result_url)
                response = view(request, *args, **kwargs)
                if hasattr(response, 'render'):
                    response.render()
                # All saving views in this project use POST/redirect/GET.
                # Admin confirmation and validation pages must remain retryable.
                if response.status_code not in (302, 303):
                    transaction.set_rollback(True)
                else:
                    submission.result_url = response['Location']
                    submission.save(update_fields=['result_url'])
                return response
        except OperationalError as error:
            if 'locked' not in str(error).lower():
                raise
            response = HttpResponse('Сохранение уже выполняется. Вернитесь назад и повторите отправку через несколько секунд.', status=503)
            response['Retry-After'] = '2'
            return response

    def process_response(self, request, response):
        if (response.streaming or response.status_code != 200
                or not response.get('Content-Type', '').startswith('text/html')
                or response.get('Content-Encoding') or not hasattr(request, 'user')):
            return response
        parser = FormTokens(response.content.decode(response.charset), request)
        parser.feed(parser.source)
        response.content = parser.output().encode(response.charset)
        if response.has_header('Content-Length'):
            response['Content-Length'] = str(len(response.content))
        patch_cache_control(response, private=True, no_store=True)
        return response
