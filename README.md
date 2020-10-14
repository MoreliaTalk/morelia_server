# Morelia Server - мессенджер (сервер) для Morelia Network #

![]() *тут скриншот*

## В репозитории 2 бранча ##

[master](https://github.com/MoreliaTalk/morelia_server/tree/master) - Основная и стабильная ветка.

[master-develop](https://github.com/MoreliaTalk/morelia_server/tree/develop) - Ветка для добавления нового функционала.

## В разработке применяется ##

* [Python 3.8](https://www.python.org/) - язык программирования

* [FastAPI](https://fastapi.tiangolo.com) - основной фреймворк

* [SQLObject](http://sqlobject.org) - ORM для работы с базой данный

* [Pydantic](https://pydantic-docs.helpmanual.io) - валидация данных

* [Starlette](https://www.starlette.io) - лёгковесный ASGI фреймворк/тулкит.

## Описание репозитория ##

* /mod
  * api.py - модуль отвечает за описание АПИ, а так же валидацию данных.
  * config.py - модуль отвечает за хранение настроек (констант).
  * controller.py - модуль отвечает за реализацию методов описанных в [Morelia Protocol](https://github.com/MoreliaTalk/morelia_protocol/blob/master/README.md)
  * lib.py - модуль отвечает за хэширования пароля, сравнения пароля с его хэш-суммой, создание хэша для auth_id.
  * models.py - модуль отвечает за описание таблиц БД для работы через ОРМ.

* /templates - шаблоны для вывода статистики сервера в браузере
  * base.html - базовый шаблон с основными элементами меню, он имплементируется в каждый рабочий шаблон
  * index.html - рабочий шаблон главной страницы
  * status.thml - рабочий шаблон страницы со статусом работы сервера

* /settings
  * logging.py - настройки логирования

* server.py - основной код сервера

* manage.py - менеджер миграции для БД

* /tests
  * fixtures/
    * api.json - json-файл с заранее подготовленными данными, для провдедения тестов
  * test_api.py - тесты для проверки валидации
  * test_controller.py - тесты для проверки класса который отвечает за обработкуметодов протокола
  * test_lib.py - тесты хэш-функции

* debug_server.py - обёртка для server.py для дебага через утилиту `pdb`

## Установка ##

Установить [Python](https://www.python.org/downloads/) версии 3.8.

Загрузить и установить последнюю версию [git](https://git-scm.com/downloads).

Если нужен GUI, установить [GitHub Desktop](https://desktop.github.com/).

Настроить Git или GitHub Desktop введя свои `username` и `email` от аккаунта созданного на [github](https://www.github.com).

## Форк репозитория Morelia Server ##

Если ты не включен в команду на GitHub'е проекта, то необходимо сначала форкнуть к себе репозиторий Morelia Server перейдя по [ссылке](https://github.com/MoreliaTalk/morelia_server/fork).

## Клонирование репозитория на локальный компьютер ##

Клонировать репозиторий к себе на локальный компьютер используя командную строку и `git`

```cmd
git clone https://github.com/{username}/morelia_server.git
cd morelia_server
```

Переключаемся на ветку develop

```cmd
git checkout develop
```

Синхронизируем свой форк с оригинальным репозиторием `upstream` Morelia Server

```cmd
git remote add upstream https://github.com/MoreliaTalk/morelia_server.git
```

Проверяем появились ли репозиторий `upstream` в списке удалённых репозиториев

```cmd
git remote -v
> origin    https://github.com/{username}/morelia_server.git (fetch)
> origin    https://github.com/{username}/morelia_server.git (push)
> upstream  https://github.com/MoreliaTalk/morelia_server.git (fetch)
> upstream  https://github.com/MoreliaTalk/morelia_server.git (push)
```

При использовании `GitHub` выбрать в меню `File` пункт `Clone repository...` далее следовать инструкциям

## Настройка виртуального окружения Pipenv ##

Для работы с проектом необходима установка библиотек которые он использует, т.н. `рабочее окружение`, для этого используется утилита [Pipenv](https://github.com/pypa/pipenv)

Если не установлен pipenv, выполнить

```cmd
python -m pip install pipenv
```

Создать виртуальное окружение в директории с проектом

```cmd
pipenv shell
```

Установить все требуемые библиотеки из Pipfile

```cmd
pipenv install --ignore-pipfile
```

## Запуск сервера ##

Перед запуском необходимо создать базу данных с пустыми таблицами, командой

```cmd
python ./manage.py --table create
```

Дополнительно можно добавить первого пользователя в таблицу

```cmd
python ./manage.py --table superuser
```

Для дополнительной информации о возможностях менеджера миграций

```cmd
python ./manage.py --help
```

Для запуска сервера используйте команду

```cmd
uvicorn server:app --host 0.0.0.0 --port 8000 --reload --use-colors --http h11 --ws websockets
```

Дополнительные параметры которые можно передать серверу:

`--log-level <str>` - Set the log level. Options: 'critical', 'error', 'warning', 'info', 'debug', 'trace'. Default: 'info'.

`--use-colors / --no-use-colors` - Enable / disable colorized formatting of the log records, in case this is not set it will be auto-detected. This option is ignored if the `--log-config` CLI option is used.

`--loop <str>` - Set the event loop implementation. The uvloop implementation provides greater performance, but is not compatible with Windows or PyPy. Options: 'auto', 'asyncio', 'uvloop'. Default: 'auto'.

`--http <str>` - Set the HTTP protocol implementation. The httptools implementation provides greater performance, but it not compatible with PyPy, and requires compilation on Windows. Options: 'auto', 'h11', 'httptools'. Default: 'auto'.

`--ws <str>` - Set the WebSockets protocol implementation. Either of the websockets and wsproto packages are supported. Use 'none' to deny all websocket requests. Options: 'auto', 'none', 'websockets', 'wsproto'. Default: 'auto'.

`--lifespan <str>` - Set the Lifespan protocol implementation. Options: 'auto', 'on', 'off'. Default: 'auto'.

`--interface` - Select ASGI3, ASGI2, or WSGI as the application interface. Note that WSGI mode always disables WebSocket support, as it is not supported by the WSGI interface. Options: 'auto', 'asgi3', 'asgi2', 'wsgi'. Default: 'auto'.

`--limit-concurrency <int>` - Maximum number of concurrent connections or tasks to allow, before issuing HTTP 503 responses. Useful for ensuring known memory usage patterns even under over-resourced loads.

`--limit-max-requests <int>` - Maximum number of requests to service before terminating the process. Useful when running together with a process manager, for preventing memory leaks from impacting long-running processes.

`--backlog <int>` - Maximum number of connections to hold in backlog. Relevant for heavy incoming traffic. Default: 2048

`--ssl-keyfile <path>` - SSL key file

`--ssl-certfile <path>` - SSL certificate file

`--ssl-version <int>` - SSL version to use (see stdlib ssl module's)

`--ssl-cert-reqs <int>` - Whether client certificate is required (see stdlib ssl module's)

`--ssl-ca-certs <str>` - CA certificates file

`--ssl-ciphers <str>` - Ciphers to use (see stdlib ssl module's)

`--timeout-keep-alive <int>` - Close Keep-Alive connections if no new data is received within this timeout. Default: 5.


## Создание пулл-реквеста для внесенния изменений в develop-ветку Morelia Server ##

Получение последних изменнений из develop-ветки Morelia Server

```cmd
git pull upstream develop
```

Отправка изменений в develop-ветку своего форка

```cmd
git push
```

Для создания пулл-реквеста, необходимо перейти на [GitHub](https://www.github.com), выбрать свой форк и в правом меню нажать на `New pull request`, после чего выбрать бранч из которого будет производится перенос изменений в develop-ветку Morelia Qt и нажать `Create pull request`.

## Требования к стилю кода ##

Перед началом работы рекомендуется прочитать [PEP 8 - руководство по написанию кода на Python](https://pythonworld.ru/osnovy/pep-8-rukovodstvo-po-napisaniyu-koda-na-python.html). Обязательно использовать линтер (flake8, pylint или подобный).

## Логирование ##

Используется библиотека [loguru](https://github.com/Delgan/loguru)

Уровни логирования которыми можно пользоваться в коде:

```py
Level name | Logger method

DEBUG      | logger.debug()
INFO       | logger.info()
SUCCESS    | logger.success()
WARNING    | logger.warning()
ERROR      | logger.error()
CRITICAL   | logger.critical()
```

Для включения **DEBUG** режима, запускать сервер с параметром:

```cmd
uvicorn server:app --log-level debug
```

## Написание и запуск тестов ##

Для написания тестов используется встроенный модуль Unittest.

Для запуска тестов выполните (вместо звёздочки подставьте наименование теста)

```cmd
python -v ./tests/test_*.py
```

## Запуск дебаггера ##

Для запуска дебаггера в полевых условиях, через консоль

```cmd
python -m pdb ./debug_server.py
```

Для получения справки в дебаг-режиме

```cmd
(pdb) help
```

## Контакты ##

[Telegram](https://t.me/joinchat/LImHShzAmIWvpMxDTr5Vxw) - группа где обсуждаются насущные вопросы.

[Trello](https://trello.com/b/qXjJFTP3/develop) - kanban-доска для проекта.

[Slack](www.moreliatalk.slack.com) - альтернативный вариант обсуждения проекта.
