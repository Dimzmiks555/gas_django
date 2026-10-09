FROM python:3.13-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=app.settings_docker
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && groupadd --gid 10001 gas \
    && useradd --uid 10001 --gid gas --no-create-home gas
COPY app ./app
COPY gas ./gas
COPY old ./old
COPY docx ./docx
COPY manage.py ./
COPY docker/entrypoint.sh /entrypoint.sh
RUN mkdir -p /data/generated_docs /app/staticfiles \
    && chown -R gas:gas /data /app/staticfiles \
    && chmod 755 /entrypoint.sh
USER gas
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "app.wsgi:application", "--no-control-socket", "--bind", "0.0.0.0:8000", "--workers", "1", "--worker-class", "gthread", "--threads", "4", "--timeout", "30", "--keep-alive", "5", "--access-logfile", "-", "--error-logfile", "-"]
