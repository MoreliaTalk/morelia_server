# Morelia Server - мессенджер (сервер) для Morelia Network #

Language [EN](./README_ENG.md), [RU](./README.md)

## В репозитории 2 бранча ##

[Master](https://github.com/MoreliaTalk/morelia_server/tree/master) - стабильная ветка.

[Develop](https://github.com/MoreliaTalk/morelia_server/tree/develop) - ветка для добавления нового функционала.

## В разработке применяется ##

* [Python 3.10](https://www.python.org/) - язык программирования

* [FastAPI](https://fastapi.tiangolo.com) - основной фреймворк

* [SQLObject](http://sqlobject.org) - ORM для работы с базой данный

* [Pydantic](https://pydantic-docs.helpmanual.io) - валидация данных

* [Starlette](https://www.starlette.io) - легковесный ASGI фреймворк/тулкит

* [websockets](https://pypi.org/project/websockets/) - реализация протокола Websockets в Python (RFC 6455 & 7692)

## Описание репозитория ##

* /admin
  * /templates - шаблоны страниц админки
  * admin.py
  * control.py
  * login.py
  * logs.py
* /mod
  * /db
    * dbhandler.py - модуль предназначен для выполнения запросов к БД
    * models.py - модуль отвечает за описание таблиц БД для работы через ОРМ.
  * /protocol
    * /matrix
      * api.py - модуль отвечает за описание API, а так же валидацию данных.
      * worker.py - реализация протокола
    * /mtp
      * api.py - модуль отвечает за описание API, а так же валидацию данных.
      * worker.py - модуль отвечает за реализацию методов описанных в [Morelia Protocol](https://github.com/MoreliaTalk/morelia_protocol/blob/master/README.md).
    * error.py - модуль отвечает за проверку и генерацию ответов с кодами ошибок.
    * controller.py - модуль обрабатывает запрос в соответствии с типом протокола
    * lib.py - модуль отвечает за хеширование пароля, сравнения пароля с его хэш-суммой, создание хеша для auth_id.
    * logging.py - модуль настройки логирования.
    * config.py - модуль читает настройки из config.ini
* /static - 
* server.py - основной код сервера
* manage.py - менеджер миграции для БД (создание и удаление таблиц базы данных)
* /tests
  * fixtures/ - json-файлы с заранее подготовленными данными, для проведения тестов.
  * config.ini - конфиг сервера для проведения тестов
  * test_*.py - тесты
* debug_server.py - обёртка для server.py для дебага через утилиту `pdb`.
* example_config.ini - файл содержащий пример настроек сервера, перед запуском сервера просто переименуйте в `config.ini`.
* client.py - мини-клиент для проверки работы сервера.

## Установка ##

Установить [Python](https://www.python.org/downloads/) версией 3.10 или выше.

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

Для работы с проектом необходимо установить библиотеки которые он использует и настроить т.н. `виртуальное рабочее окружение` или `virtualenv`, для этого используется утилита [Pipenv](https://github.com/pypa/pipenv)

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

## Перед запуском сервера - используем менеджер настроек ##

Перед запуском сервера необходимо выполнить некоторые настройки (создать БД, таблицы и добавить первого пользователя - администратора)

Откройте файл `example_config.ini`, найдите параметр URI, замените его на путь к базе данных, пример:
`URI = 'sqlite:db_sqlite.db' `, сохраните файл как `config.ini`

Создаём базу данных с пустыми таблицами:

```cmd
pipenv run python ./manage.py --db create
```

Если необходимо удалить все таблицы в созданной базе данных (ВНИМАНИЕ удаляются только таблицы, БД не удаляется):

```cmd
pipenv run pipenv run python ./manage.py --db delete
```

Добавляем администратора в созданную БД:

```cmd
python ./manage.py superuser-create
```

Дополнительно можно создать `flow` с типом группа:

```cmd
pipenv run python ./manage.py --table flow
```

Информация о всех возможностях менеджера настроек:

```cmd
pipenv run python ./manage.py --help
```

## Запуск сервера ##

Для запуска сервера используйте команду:

```cmd
uvicorn server:app --host 0.0.0.0 --port 8000 --reload --use-colors --http h11 --ws websockets
```

Дополнительные параметры которые можно передать серверу:

`--log-level <str>` - Set the log level. Options: 'critical', 'error', 'warning', 'info', 'debug', 'trace'. Default: 'info'.

`--use-colors / --no-use-colors` - Enable / disable colorized formatting of the log records, in case this is not set it will be auto-detected. This option is ignored if the `--log-config` CLI option is used.

`--loop <str>` - Set the event loop implementation. The uvloop implementation provides greater performance, but is not compatible with Windows or PyPy. Options: 'auto', 'asyncio', 'uvloop'. Default: 'auto'.

`--http <str>` - Set the HTTP protocol implementation. The httptools implementation provides greater performance, but it is not compatible with PyPy, and requires compilation on Windows. Options: 'auto', 'h11', 'httptools'. Default: 'auto'.

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

## Запуск сервера в режиме DEBUG ##

Для лёгкого запуска сервера в режиме отладки нужно всего лишь запустить `debug_server.py`:

```cmd
pipenv run python ./debug_server.py
```

## Проверка работоспособности сервера с помощью встроенного клиента ##

Для проверки работы сервера запустите мини-клиент `client.py` в консоли:

```cmd
pipenv run python -i ./client.py
```

После запуска клиент отправит на сервер сообщение об авторизации (AUTH), ответ сервера будет выведен в консоль, после чего `python` перейдёт в режим интерактивной строки `>>>`, для того чтобы была возможность провести дополнительные проверки.

В интерактивной консоли будет доступна одна функция отправки сообщений `send_message` которая принимает два аргумента `message`-сообщение и `uri`-адрес сервера. В аргументе `message` необходимо передать объект с типом "dict" или "str", можно использовать готовые примеры запросов: AUTH, GET_UPDATE, ADD_FLOW, ALL_FLOW. В аргументе необходимо передать объект с типом "str", можно использовать готовый пример адреса сервера: LOCALHOST.

```py
>>> send_message(GET_UPDATE, LOCALHOST)
```

Если в функцию не передать ни одного аргумента, по умолчанию будет отправлено сообщение AUTH на LOCALHOST.

## Создание пулл-реквеста для внесения изменений в develop-ветку Morelia Server ##

Получение последних изменений из develop-ветки Morelia Server

```cmd
git pull upstream develop
```

Отправка изменений в develop-ветку своего форка

```cmd
git push
```

Для создания пулл-реквеста, необходимо перейти на [GitHub](https://www.github.com), выбрать свой форк и в правом меню нажать на `New pull request`, после чего выбрать бранч из которого будет производиться перенос изменений в develop-ветку Morelia Server и нажать `Create pull request`.

## Требования к стилю кода ##

Перед началом работы рекомендуется прочитать [PEP 8 - руководство по написанию кода на Python](https://pythonworld.ru/osnovy/pep-8-rukovodstvo-po-napisaniyu-koda-na-python.html). Обязательно использовать линтер (flake8, pylint или подобный).

## Логирование ##

Используется библиотека [loguru](https://github.com/Delgan/loguru)

Уровни логирования которыми можно пользоваться в коде:

```
Level name | Logger method

DEBUG      | logger.debug()
INFO       | logger.info()
SUCCESS    | logger.success()
WARNING    | logger.warning()
ERROR      | logger.error()
           | logger.exception()
CRITICAL   | logger.critical()
```

## Написание и запуск тестов ##

Для написания тестов используется встроенный модуль Unittest.

Для запуска тестов выполните (вместо звёздочки подставьте наименование теста)

```cmd
pipenv run python -v ./tests/test_*.py
```

## Запуск дебагера ##

Для запуска дебагера в полевых условиях, через консоль

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

## Лицензия ##

Copyright (c) 2020 - настоящее время [NekrodNIK](https://github.com/NekrodNIK), [Stepan Skriabin](https://github.com/stepanskryabin), [rus-ai](https://github.com/rus-ai) и другие. Смотрите полный список в файле AUTHORS.md.

Morelia Server находится под лицензией GNU Lesser General Public License версии 3 или более поздней(LGPL-3.0-or-later). Подробности смотрите в файле COPYING.LESSER.
