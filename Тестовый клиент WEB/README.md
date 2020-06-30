# Morelia Web - мессенджер (клиент) #
-----------------------------------------------------------

## В репозитории 2 бранча: ##

[master](https://github.com/MoreliaTalk/morelia_client_web/tree/master) - Основная ветка.

[develop](https://github.com/MoreliaTalk/morelia_client_web/tree/develop) - Ветка для разработчиков.

## В разработке применяется: ##

* [JavaScript](https://developer.mozilla.org/ru/docs/Web/JavaScript)
* [HTML](https://developer.mozilla.org/ru/docs/Web/HTML)
* [CSS](https://developer.mozilla.org/ru/docs/Web/CSS)


## Установка ##

Загрузить и установить последнюю версию [git](https://git-scm.com/downloads).

Если нужен GUI установить [GitHub Desktop](https://desktop.github.com/).

Настроить Git или GitHub Desktop введя свои `username` и `email` от аккаунта созданного на [github](https://www.github.com).

Форкнуть к себе репозиторий Morelia Web перейдя по ссылке [Fork](https://github.com/MoreliaTalk/morelia_client_web/fork).

Клонировать репозиторий к себе на локальный компьютер [Clone](https://github.com/MoreliaTalk/morelia_client_web.git).
```
git clone https://github.com/MoreliaTalk/morelia_client_web.git
cd morelia-qt
```

Добавит свой форк. Заменить `{username}` на свой username созданный в гитхабе.
```
git remote add fork https://github.com/{username}/morelia_client_web.git
```

Создать виртуальное окружение (предварительно установить pipenv).
```
pipenv shell
```

Установите все необходимые библиотеки
```
pipenv update
```

Если используется pip, то установить библиотеки следующим образом
```
pip install -r requirements.txt
```

Создаем свой бранч со своим именем
```
git branch {имя бранча}
```

### Начинай кодить! ###

Для добавления своего кода в ветку [develop](https://github.com/MoreliaTalk/morelia_client_web/tree/develop)
```
git pull request origin develop
```

## Требования к стилю кода ##

Перед началом работы рекомендуется прочитать [Руководство по написанию кода на JavaScript](). Обязательно использовать линтер (eslinter или подобный).

### дополнительные требования к коду ###
Отсутствуют



---------------------------------------------------------------------------------------------------------------------

## Контакты: ##

[Telegram](https://t.me/joinchat/LImHShzAmIWvpMxDTr5Vxw) - группа где обсуждаются насущные вопросы.

[Trello](https://trello.com/b/qXjJFTP3/develop) - kanban-доска для проекта.
