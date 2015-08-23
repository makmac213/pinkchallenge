from django.conf.urls import patterns, include, url
from django.conf import settings

# frontend
from .views import ChatView


urlpatterns = patterns('',
    url(r'^$', 
            ChatView.SendRequest.as_view(), 
            name='send_request'),
    url(r'^$', 
            ChatView.CheckRequestNotifications.as_view(), 
            name='check_request_notifications'),
)