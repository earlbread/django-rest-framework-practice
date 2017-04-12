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

## 3. Creating a model to work with

Add code below to `snippets/models.py`.

```python
from django.db import models
from pygments.lexers import get_all_lexers, get_lexer_by_name
from pygments.styles import get_all_styles
from pygments.formatters.html import HtmlFormatter
from pygments import highlight

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted((item, item) for item in get_all_styles())

class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)
    owner = models.ForeignKey('auth.User', related_name='snippets', on_delete=models.CASCADE)
    highlighted = models.TextField()

    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML
        representation of the code snippet.
        """
        lexer = get_lexer_by_name(self.language)
        linenos = self.linenos and 'table' or False
        options = self.title and {'title': self.title} or {}
        formatter = HtmlFormatter(style=self.style, linenos=linenos,
                                  full=True, **options)
        self.highlighted = highlight(self.code, lexer, formatter)
        super(Snippet, self).save(*args, **kwargs)

    class Meta:
        ordering = ('created',)
```

We'll also need to create an initial migration for our snippet model, and sync the database for the first time.
```bash
python manage.py makemigrations snippets
python manage.py migration
```

## 4. Creating a Serializer class

Add code below to `snippets/serializers.py`.

```python
from rest_framework import serializers
from snippets.models import Snippet


class SnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snippet
        fields = ('id', 'title', 'code', 'linenos', 'language', 'style')
```

## 5. Writing views using generic class-based view.

Edit the `snippets/views.py` file, and add the following.

```python
from rest_framework import generics
from snippets.models import Snippet
from snippets.serializers import SnippetSerializer

class SnippetList(generics.ListCreateAPIView):
    """
    List all code snippets, or create a new snippet.
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer

class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a code snippet.
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
```

Also we need to wire these views up. Create the `snippets/urls.py` file:

```python
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from snippets import views

urlpatterns = [
        url(r'^snippets/$', views.SnippetList.as_view()),
        url(r'^snippets/(?P<pk>[0-9]+)/$', views.SnippetDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
```

We also need to wire up the root urlconf, in the `pastebin/urls.py` file to include our snippet app's URLs.

```python
from django.conf.urls import url, include

urlpatterns = [
    url(r'^', include('snippets.urls')),
]
```
