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

* /old/database
  * main.py - прямая работа с БД SQLite3

* /mod
  * api.py - модуль отвечает за описание АПИ, а так же валидацию данных.
  * config.py - модуль отвечает за хранение настроек (констант).
  * controller.py - модуль отвечает за реализацию методов описанных в [Morelia Protocol](https://github.com/MoreliaTalk/morelia_protocol/blob/master/README.md)
  * libhash.py - модуль отвечает за хэширования пароля, сравнения пароля с его хэш-суммой, создание хэша для auth_id.
  * models.py - модуль отвечает за описание таблиц БД для работы через ОРМ.

* /templates - шаблоны для вывода статистики сервера в браузере

* /settings - настройки логирования

* app.py - основной код сервера

* manage.py - менеджер миграции для БД

* settings.py - настройки логирования

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

*В случае если работать необходимо не через ОРМ SQLObject, а напрямую с базой данных SQLite,
необходимо раскомментировать строчку №18 и закомментировать строчки №22, 23, 27, 28 в файле app.py*

Перед запуском необходимо создать базу данных с пустыми таблицами, командой

```cmd
python ./manage.py --table create
```

Для запуска используйте команду

```cmd
python ./app.py
```

Для дополнительной информации о возможностях менеджера миграций

```cmd
python ./manage.py --help
```

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

Уровни логирования которыми 
можно пользоваться в коде:
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
uvicorn app:app --log-level debug
``` 
## Контакты ##

[Telegram](https://t.me/joinchat/LImHShzAmIWvpMxDTr5Vxw) - группа где обсуждаются насущные вопросы.

[Trello](https://trello.com/b/qXjJFTP3/develop) - kanban-доска для проекта.

[Slack](www.moreliatalk.slack.com) - альтернативный вариант обсуждения проекта.
