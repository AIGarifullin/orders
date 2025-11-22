# Приложение orders
Тестовый проект: мини-сервис аналитики заказов

## Стек проекта
Python, Django REST Framework, HTTPS, PostgreSQL, Postman


## Установка и запуск
💡 ВЕРСИЯ Python 3.13

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас Windows (в Git Bash)

    ```
    source env/Scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Создать суперпользователя:

```
python3 manage.py createsuperuser
```

Запустить проект:

```
python3 manage.py runserver
```
