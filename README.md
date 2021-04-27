# kesha

kesha is an accounting helper for django.
It provides the necessary models and view and is ready to be included into your project.

![django_kesha_logo](assets/django-kesha-logo.png?raw=true "django-kesha-logo")

## Idea

I need an accounting tool, but I don't like Gnucash. I want to link documents to each booking,
and the whole thing should be somewhat auditproof. I could not find any tool that suits these
needs, therefore I started writing my own tools. Previously I worked on [kescher](https://github.com/westnetz/kescher) which is the proof of concept for this application. It has some major flaws, (e.g. i does not calculate correctly) but this will be fixed with this app.

## Features

_Django-kesha_ currently provides some basic accounting functionality. 

## Related apps

* [django-doma](https://github.com/olf42/django-doma) - Simple Document Management App
* [django-afa](https://github.com/olf42/django-afa) - Aufwendungen für Abschreibungen Helper

Tested with the following versions of Python/Django:

* Django: 2.2, 3.0, 3.1, 3.2
* Python: 3.7, 3.8, 3.9

## Installation

Install `django-kesha` using pip:

```zsh
$ pip install django-kesha
```

## Quick start

1. Add "kesha" to your INSTALLED_APPS setting like this::

```python
INSTALLED_APPS = [
    ...
    "kesha",
]
```

2. Include the polls URLconf in your project urls.py like this::

    path('kesha/', include('kesha.urls')),

3. Run ``python manage.py migrate`` to create the kesha models.

4. Visit http://127.0.0.1:8000/kesha/ to start accounting.
