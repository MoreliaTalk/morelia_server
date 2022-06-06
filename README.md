# Morelia Server - сервер для мессенджера MoreliaTalk #


![tests](https://github.com/MoreliaTalk/morelia_server/workflows/Test%20and%20Linting/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/MoreliaTalk/morelia_server/badge.svg?branch=master)](https://coveralls.io/github/MoreliaTalk/morelia_server)

Language [EN](./README_ENG.md), [RU](./README.md)

## В репозитории 2 бранча ##

[Master](https://github.com/MoreliaTalk/morelia_server/tree/master) - стабильная ветка.

## В разработке применяется ##

* [Python 3.10](https://www.python.org/) - язык программирования

* [Starlette](https://www.starlette.io/) - основной фреймворк

* [SQLObject](http://sqlobject.org) - ORM для работы с базой данный

* [Pydantic](https://pydantic-docs.helpmanual.io) - валидация данных

* [Starlette](https://www.starlette.io) - легковесный ASGI фреймворк/тулкит

* [websockets](https://pypi.org/project/websockets/) - реализация протокола Websockets в Python (RFC 6455 & 7692)

## Описание репозитория ##

* /mod
  * /config
    * config.py - модуль отвечает за работу с конфигурационным файлом config.ini
    * validator.py - модуль для валидации конфигурационного файла
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
    * log_handler.py - модуль настройки логирования.
    * config.py - модуль читает настройки из config.ini
* server.py - основной код сервера
* manage.py - cli-инструмент для работы с сервером(запуск, тестовый клиент, работа с бд, и т.п.)
* /tests
  * fixtures/ - json-файлы с заранее подготовленными данными, для проведения тестов.
  * config.ini - конфиг сервера для проведения тестов
  * test_*.py - тесты
* example_config.ini - файл содержащий пример настроек сервера, перед запуском сервера просто переименуйте или скопируйте в `config.ini`.

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
`URI = 'sqlite:db_sqlite.db' `

Создание `config.ini`, файла БД и учётной записи администратора сервера:

```cmd
pipenv run python ./manage.py run init
```

Если необходимо удалить все таблицы в созданной базе данных (ВНИМАНИЕ удаляются только таблицы, БД не удаляется):

```cmd
pipenv run python ./manage.py delete db
```

Дополнительно можно создать тестовый `flow`:

```cmd
pipenv run python ./manage.py create flow
```

Информация о всех возможностях менеджера настроек:

```cmd
pipenv run python ./manage.py --help
```

## Запуск сервера в режиме отладки ##

Для запуска сервера используйте команду:

```cmd
pipenv run python ./manage.py run devserver
```

## Запуск сервера в нормально режиме работы ##

Для запуска сервера используйте команду:

```cmd
pipenv run python ./manage.py run server
```

Параметры которые можно передать серверу (и в режиме отладки и в нормальном режиме):

`--host <str>` - адрес сервера, по умолчанию 127.0.0.1.

`--port <int>` - порт серврера, по умолчанию 8080.

`--log-level <str>` - уровень логирования: critical, error, warning, info, debugб trace, по умолчанию debug.

`--use-colors` - включить использования цветного вывода сообщений.

`--reload` - "горячая" перезагрузка.


## Проверка работоспособности сервера с помощью встроенного клиента ##

Для проверки работы сервера запустите встроенный в `manage.py` мини-клиент:

```cmd
pipenv run python manage.py client send
```

Примечание: перед запуском клиента нужно запустить сервер

## Создание пулл-реквеста для внесения изменений в master-ветку Morelia Server ##

Получение последних изменений из master-ветки Morelia Server

```cmd
git pull upstream master
```

Отправка изменений в master-ветку своего форка

```cmd
git push
```

Для создания пулл-реквеста, необходимо перейти на [GitHub](https://www.github.com), выбрать свой форк и в правом меню нажать на `New pull request`, после чего выбрать ветвь из которого будет производиться перенос изменений в master-ветку Morelia Server и нажать `Create pull request`.

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

## Контакты ##

[Telegram](https://t.me/+xfohB6gWiOU5YTUy) - группа для связи с разработчиками.

[Slack](moreliatalk.slack.com) - дополнительный канал для связи с разработчиками.

## Лицензия ##

Copyright (c) 2020 - настоящее время MoreliaTalk team
  [NekrodNIK](https://github.com/NekrodNIK),
  [Stepan Skriabin](https://github.com/stepanskryabin),
  [rus-ai](https://github.com/rus-ai) и другие.
  Смотрите полный список в файле AUTHORS.md.

Morelia Server находится под лицензией GNU Lesser General Public License версии 3 или более поздней(LGPL-3.0-or-later). Подробности смотрите в файле COPYING.LESSER.
