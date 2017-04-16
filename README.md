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
from django.contrib.auth.models import User
from rest_framework import serializers
from snippets.models import Snippet


class SnippetSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    highlight = serializers.HyperlinkedIdentityField(view_name='snippet-highlight',
                                                     format='html')

    class Meta:
        model = Snippet
        fields = ('url', 'id', 'highlight', 'title', 'code', 'linenos', 'language', 'style', 'owner')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    snippets = serializers.HyperlinkedRelatedField(many=True, view_name='snippet-detail', read_only=True)

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'snippets')
```

## 5. Writing views using ViewSet.

Edit the `snippets/views.py` file, and add the following.

```python
from django.contrib.auth.models import User
from rest_framework import permissions, renderers, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import detail_route
from snippets.models import Snippet
from snippets.serializers import SnippetSerializer, UserSerializer
from snippets.permissions import IsOwnerOrReadOnly


class SnippetViewSet(viewsets.ModelViewSet):
    """
    This view set automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    @detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This view set automatically provides `list` and `detail` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class APIRoot(APIView):
    def get(self, request, format=None):
        return Response({
            'users': reverse('user-list', request=request, format=format),
            'snippets': reverse('snippet-list', request=request, format=format),
        })
```

Also we need to wire these views up. Create the `snippets/urls.py` file:

```python
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from snippets import views
from snippets.views import SnippetViewSet, UserViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'snippets', views.SnippetViewSet)
router.register(r'users', views.UserViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth', include('rest_framework.urls', namespace='rest_framework'))
]
```

We also need to wire up the root urlconf, in the `pastebin/urls.py` file to include our snippet app's URLs.

```python
from django.conf.urls import url, include

urlpatterns = [
    url(r'^', include('snippets.urls')),
    url(r'^api-auth/', include('rest_framework.urls',
                                namespace='rest_framework')),
]
```
