from django.conf.urls import patterns, include, url
from django.conf import settings

# frontend
from .views import ChatView


urlpatterns = patterns('',
    url(r'^send-request/$', 
            ChatView.SendRequest.as_view(), 
            name='send_request'),
    url(r'^accept-request/$', 
            ChatView.AcceptRequest.as_view(), 
            name='accept_request'),
    url(r'^check-request-notifications/$', 
            ChatView.CheckRequestNotifications.as_view(), 
            name='check_request_notifications'),
    url(r'^check-request-status/$', 
            ChatView.CheckRequestStatus.as_view(), 
            name='check_request_status'),

)