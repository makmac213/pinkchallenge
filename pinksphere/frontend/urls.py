from django.conf.urls import patterns, include, url
from django.conf import settings

# frontend
from .views import FrontendView


urlpatterns = patterns('',
    url(r'^$', FrontendView.Index.as_view(), name='index'),
    url(r'^login/$', FrontendView.Login.as_view(), name='login'),
    url(r'^logout/$', FrontendView.Logout.as_view(), name='logout'),
)