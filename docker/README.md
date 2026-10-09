# Запуск GAS в Docker

Образ: Python 3.13, Django 5.2, Gunicorn (один процесс, четыре потока для параллельных соединений), WhiteNoise.
Compose публикует только `127.0.0.1:8001`. Данные хранятся в volume `app_data`:
`/data/db.sqlite3` и `/data/generated_docs`. Образ не содержит локальную БД,
готовые документы, `.env`, Windows venv или Git-историю.

## Первый запуск

В каталоге проекта на сервере (команды Docker при необходимости выполнять через sudo):

```sh
cp .env.example .env
python3 - <<'PY'
from pathlib import Path
import secrets
p = Path('.env')
p.write_text(p.read_text().replace('DJANGO_SECRET_KEY=\n', 'DJANGO_SECRET_KEY=' + secrets.token_urlsafe(64) + '\n'))
p.chmod(0o600)
PY
docker compose build
docker compose up -d
docker compose ps
docker compose logs --tail=100 web
docker compose exec web python manage.py createsuperuser
```

Повторно не копируйте `.env.example` поверх заполненного `.env`: ключ должен
сохраняться между перезапусками. При старте выполняются check, migrate и collectstatic;
при ошибке сервер не запускается. Команды `compose run` и `exec` не выполняют
миграции автоматически. Пустая БД не содержит справочников оборудования и цен:
их нужно заполнить через админку перед созданием договоров (см. основной readme).

На своём компьютере:

```sh
ssh -N -L 8001:127.0.0.1:8001 boss@192.168.0.150
```

Открыть http://localhost:8001/accounts/login/ или http://localhost:8001/admin/.
Порт 8080 существующего сервиса не используется.

## Перенос существующих данных вместо пустой БД

Сначала сделайте согласованную копию исходной SQLite через sqlite3 backup API
(или остановите исходное приложение на время копирования). Переносите также весь
каталог generated_docs. Не добавляйте данные в Docker-образ.

Для НОВОГО volume до первого `up` положите копию БД в `seed/db.sqlite3`, а документы
в `seed/generated_docs/`, затем выполните:

```sh
docker compose run --rm --user root --cap-add DAC_OVERRIDE --cap-add CHOWN --cap-add FOWNER -v "$PWD/seed:/seed:ro" web sh -ec '
  test ! -e /data/db.sqlite3
  cp /seed/db.sqlite3 /data/db.sqlite3
  cp -R /seed/generated_docs/. /data/generated_docs/
  chown -R 10001:10001 /data
'
docker compose up -d
```

Команда отказывается заменять уже существующую БД. Если копирование завершилось
ошибкой, проверьте частично скопированные данные перед повтором. Старые имена
документов сохраняются; известное несоответствие старых имён текущим обработчикам
скачивания этим переносом не исправляется.

## Резервная копия перед обновлением

Копируйте БД и документы вместе при остановленном приложении:

```sh
mkdir -p backups
chmod 700 backups
docker compose stop web
docker compose run --rm --no-deps -T web tar -C /data -czf - . > "backups/data-$(date +%Y%m%d-%H%M%S).tar.gz"
docker compose up -d
```

Проверяйте код завершения архивации и содержимое архива. Храните отдельную
защищённую копию `.env`. Восстановление: остановить web, развернуть архив в новый
volume, установить владельца 10001:10001, запустить совместимую версию образа.
Не запускайте `docker compose down -v`: ключ `-v` удаляет данные.

## Обновление и проверки

```sh
docker compose build
docker compose run --rm web python manage.py makemigrations --check --dry-run
docker compose run --rm web python manage.py test gas
docker compose up -d
docker compose ps
```

Новые миграции 0017–0019 из старой папки теперь не исключаются `.gitignore`;
добавляйте их вместе с остальными файлами при коммите. 0020 согласует модели и
миграции, включая callable для даты по умолчанию.

Контейнерный режим использует `app.settings_docker`, отключает legacy `/import/`
и требует входа для страниц приложения, кроме healthcheck и стандартных
публичных страниц авторизации Django. Статика раздаётся WhiteNoise согласно
https://whitenoise.readthedocs.io/en/stable/django.html.

Это упаковка приложения, а не исправление всех результатов ревью: остаются
проблемы расчётов, транзакций, имён документов и GET-изменения данных после входа.
Для публичного запуска отдельно нужны исправления, TLS и настройки доверенного
reverse proxy; текущая конфигурация предназначена для SSH-туннеля.

## Импорт актуальной базы 2026-10-07

На сервере `/home/boss/gas_django` сохранён исходный архив
`backups/import-20261007-original.tar.gz` (БД и 1779 документов).
В актуальной БД были другие имена миграций 0017–0018. Перед импортом проверено
совпадение структуры таблиц, индексов и внешних ключей с целевой схемой;
на копии отмечены текущие 0017–0019 и применена 0020. Содержимое всех 23 таблиц
данных проверено до и после: изменений нет. Нельзя повторять `--fake` для другой
БД без отдельного сравнения схемы.

Перенесены 871 объект, 859 договоров, 844 акта и существующие пользователи.
У 14 договоров и 2 актов не найден документ с ожидаемым текущим кодом именем;
все исходные файлы перенесены без переименования.

## Cloudflare Quick Tunnel (HTTP/2)

Для доступа с телефона добавлен Compose-сервис `tunnel` в профиле `tunnel`:

```sh
docker compose --profile tunnel up -d tunnel
docker compose logs tunnel
```

Он использует сеть хоста и подключается к `http://127.0.0.1:8001` с
`--protocol http2`. Метрики доступны только на `127.0.0.1:20242`. В `.env` должны быть
точный hostname в `DJANGO_ALLOWED_HOSTS`, полный HTTPS URL в
`DJANGO_CSRF_TRUSTED_ORIGINS` и `DJANGO_BEHIND_HTTPS_PROXY=1`.
После изменения `.env` выполните `docker compose up -d --no-deps web`.
При этом включаются Secure cookies и доверие к `X-Forwarded-Proto`;
порт приложения на хосте остаётся доступен только через loopback.

Текущий адрес на сервере записан в `tunnel-url.txt`. Это временный Quick Tunnel:
после его перезапуска адрес может измениться, тогда нужно обновить hostname,
CSRF origin и файл адреса. Для постоянного адреса нужен именованный туннель.
Документация: https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/.

Остановить только внешний доступ: `docker compose --profile tunnel stop tunnel`.
Для возврата к обычному HTTP через SSH-туннель отключите
`DJANGO_BEHIND_HTTPS_PROXY` и пересоздайте web.

Проверка 2026-10-07: коннектор зарегистрирован с `protocol=http2`, однако
публичный Quick Tunnel возвращает HTTP 530 / Cloudflare 1033. Проверены версии
2026.10.0 и 2025.11.1, глобальный регион и US, bridge и host network;
устойчивый внешний доступ не подтверждён. Финальная конфигурация использует
2026.10.0 (образ закреплён digest), глобальный регион и host network.
Для завершения настройки рассматривается именованный туннель с доменом.

## Постоянный туннель gas.evmrussia.ru

Создан туннель `gas-django` (`a90ab066-b6c1-4eec-92d5-981e7458cb27`).
Маршрут в Cloudflare: `gas.evmrussia.ru` → `http://127.0.0.1:8001`.
Для постоянного туннеля используйте оба Compose-файла вместо команды Quick Tunnel:

```sh
docker compose -f compose.yaml -f compose.named-tunnel.yaml --profile tunnel up -d
docker compose -f compose.yaml -f compose.named-tunnel.yaml logs --tail 50 tunnel
```

Токен хранится только на сервере в `secrets/cloudflared-token`: владелец UID 1000,
права 600, каталог 700. Контейнер читает файл через read-only mount и работает
как UID 1000. Транспорт HTTP/2, restart policy `unless-stopped`.
Не публикуйте токен и не добавляйте его в Git или образ.

Серверный `.env` содержит `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,gas.evmrussia.ru`,
`DJANGO_CSRF_TRUSTED_ORIGINS=https://gas.evmrussia.ru` и
`DJANGO_BEHIND_HTTPS_PROXY=1`. Предыдущее состояние сохранено в
`.env.before-named-tunnel` на сервере.

Проверка 2026-10-07: readiness коннектора 200, четыре соединения HTTP/2;
страница входа с целевым Host на origin отвечает 200. Публичный HTTPS пока
недоступен: Cloudflare ещё ожидает активацию домена, DNS-проверка возвращает
`ns1.reg.ru` / `ns2.reg.ru`. Назначенные NS: `desi.ns.cloudflare.com` и
`ignacio.ns.cloudflare.com`. После активации нужна повторная проверка HTTPS.
Наличие туннеля не означает завершение полного ревью приложения.

## Tuna: рабочий доступ с 2026-10-08

Публичная страница входа: https://silver-salmon-0972.ru.tuna.am/accounts/login/.
Бесплатный постоянный поддомен аккаунта, регион ru. При первом открытии браузер
показывает страницу Tuna с кнопкой «Посетить».

```sh
docker compose -f compose.yaml -f compose.tuna.yaml --profile tuna up -d web tuna
docker compose -f compose.yaml -f compose.tuna.yaml logs --tail 50 tuna
```

Сервис описан в `compose.tuna.yaml`; образ закреплён digest, автоматический
перезапуск `unless-stopped`. Инспектор запросов отключён, HTTP перенаправляется
на HTTPS. `secrets/tuna.env` на сервере содержит `TUNA_TOKEN`, права файла 600;
секрет не включать в Git, образ или отчёт. Сервис работает как UID 1000 без
capabilities и обращается только к origin `127.0.0.1:8001`.

В серверный `.env` добавлены точный hostname Tuna в `DJANGO_ALLOWED_HOSTS` и
HTTPS origin в `DJANGO_CSRF_TRUSTED_ORIGINS`. HTTPS proxy mode включён.
Копия прежнего `.env` — `.env.before-tuna` на сервере.

Проверены открытие формы входа в браузере, GET/POST пустой формы с CSRF (200),
Secure-флаг CSRF cookie и четыре файла статики (200). Вход с паролем не проверялся.
Cloudflare-конфигурация сохранена; переход на Tuna не меняет DNS evmrussia.ru.
Документация: https://tuna.am/docs/tunnels/http/.
