from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from snippets import views

urlpatterns = [
        url(r'^$', views.APIRoot.as_view()),
        url(r'^snippets/$', views.SnippetList.as_view(), name='snippet-list'),
        url(r'^snippets/(?P<pk>[0-9]+)/$', views.SnippetDetail.as_view()),
        url(r'^users/$', views.UserList.as_view(), name='user-list'),
        url(r'^users/(?P<pk>[0-9]+)/$', views.UserList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
