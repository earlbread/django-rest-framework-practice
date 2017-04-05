# Django pastebin

This is a tutorial for Django REST framework.

## 1. Setting up a new environment

Create a new virtual environment using virtualenv.

```bash
$ mkdir django-pastebin
$ cd django-pastebin
$ virtualenv .venv
$ source .venv/bin/activate
```

Let's install our package requirements.

```bash
$ pip install django
$ pip install djangorestframework
$ pip install pygments  # We'll using this for code highlighting
```

or

```bash
$ echo "Django==1.10.6" >> requirements.txt
$ echo "djangorestframework==3.6.2" >> requirements.txt
$ echo "Pygments==2.2.0" >> requirements.txt
$ pip install -r requirements.txt
```

And activate environment again to use django-admin

```bash
$ source .venv/bin/activate
```

## 2. Getting started

To get started, let's create a new project to work with.

```bash
$ django-admin startproject pastebin .
```

Add `snippets` app and the `rest_framework` app to `INSTALLED_APPS` in pastebin/settings.py.

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'snippets.apps.SnippetsConfig',
]
```
