# kesha

kesha is an accounting helper for django.
It provides the necessary models and view and is ready to be included into your project.

Detailed documentation is in the "docs" directory.

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
