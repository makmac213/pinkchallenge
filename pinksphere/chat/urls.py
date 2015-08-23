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
    url(r'^message/new/$', 
            ChatView.NewMessage.as_view(), 
            name='new_message'),
    url(r'^message/check-new/$', 
            ChatView.CheckNewMessage.as_view(), 
            name='check_new_messages'),
    url(r'^change-status/$', 
            ChatView.ChangeChatRequestStatus.as_view(), 
            name='chat_request_change_status'),    
)