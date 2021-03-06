import json, time, os, string, requests
from datetime import datetime, timedelta, date
from copy import deepcopy
from decimal import Decimal
from time import mktime

# django
from django import forms
from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import authenticate, login, logout, get_backends
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.sessions.backends.db import Session
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Q, Count
from django.db.models.loading import get_model
from django.http import HttpResponseRedirect, QueryDict, HttpResponseForbidden
from django.shortcuts import (HttpResponse, redirect, render_to_response, 
                                get_object_or_404, render)
from django.template import RequestContext, Context, Template
from django.template.defaultfilters import floatformat, title
from django.template.loader import render_to_string
from django.utils import timezone, translation
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.views.generic import (FormView, TemplateView, DetailView, 
                                    ListView, UpdateView)

# chat
from .models import (ChatRequest, ChatQueue, MasterAvailability, Notification,
                        ChatMessage)
from .tasks import send_chat_notifications

class ChatView(object):

    class SendRequest(View):
        """
        Disciple send request (ajax)
        """

        def post(self, request, *args, **kwargs):
            context = {
                'error': False,
            }
            user_id = request.POST.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                # expire previous pending chat requests
                pending_query = Q(user=user)
                pending_query.add(Q(status=ChatRequest.STATUS_PENDING), Q.OR)
                pending_requests = ChatRequest.objects.filter(pending_query)
                for pending_request in pending_requests:
                    pending_request.status = ChatRequest.STATUS_EXPIRED
                    pending_request.save()
                # new chat request
                chat_request = ChatRequest()
                chat_request.user = user
                chat_request.generate_request_code()
                chat_request.save()
                # send to queue
                chat_queue = ChatQueue()
                chat_queue.chat_request = chat_request
                chat_queue.save()
                # send notifications
                send_chat_notifications.delay(chat_request)
                # return request id
                context['request_code'] = chat_request.request_code
                context['message'] = 'Chat request has been sent'
            except User.DoesNotExist:
                context['error'] = True
                context['message'] = 'User does not exist'
            return HttpResponse(json.dumps(context))

        @method_decorator(csrf_exempt)
        def dispatch(self, *args, **kwargs):
            return super(ChatView.SendRequest, 
                                self).dispatch(*args, **kwargs)


    class AcceptRequest(View):
        """
        Master accept the request (ajax)
        """

        def post(self, request, *args, **kwargs):
            context = {
                'error': False,
            }
            user_id = request.POST.get('user_id')
            code = request.POST.get('request_code')
            try:
                user = User.objects.get(id=user_id)
                # if request is pending aquire the task
                chat_request = ChatRequest.objects.get(request_code=code,
                                            status=ChatRequest.STATUS_PENDING)
                chat_request.accepted_by = user
                chat_request.status = ChatRequest.STATUS_ACCEPTED
                chat_request.save()
                # change the users availability
                try:
                    availability = MasterAvailability.objects.get(user=user)
                except MasterAvailability.DoesNotExist:
                    availability = MasterAvailability(user=user)
                availability.status = MasterAvailability.STATUS_ENGAGED
                availability.save()
                # delete from queue
                chat_queue = ChatQueue.objects.get(chat_request=chat_request)
                chat_queue.delete()
                # return message
                context['message'] = 'Request has been accepted'
                context['status'] = ChatRequest.STATUS_ACCEPTED
            except ChatRequest.DoesNotExist:
                context['error'] = True
                context['message'] = 'Request no longer exist'
            except User.DoesNotExist:
                context['error'] = True
                context['message'] = 'User does not exist'
            except ChatQueue.DoesNotExist:
                # ignore if this is not in the queue
                # but we should investigate why
                pass
            return HttpResponse(json.dumps(context))

        @method_decorator(csrf_exempt)
        def dispatch(self, *args, **kwargs):
            return super(ChatView.AcceptRequest, 
                                self).dispatch(*args, **kwargs)


    class ChangeChatRequestStatus(View):
        """
        (All) end chat
        """
        def post(self, request, *args, **kwargs):
            context = {
                'error': False,
            }
            request_code = request.POST.get('request_code')
            status = request.POST.get('status')
            try:
                chat_request = ChatRequest.objects.get(request_code=request_code)
                chat_request.status = status
                chat_request.save()

                msg = ''
                if status == ChatRequest.STATUS_ENDED:
                    msg = 'Session has ended'
                elif status == ChatRequest.STATUS_CANCELLED:
                    msg = 'Chat request has been cancelled'

                context['message'] = msg
                context['status'] = status
            except ChatRequest.DoesNotExist:
                context['error'] = 'Request no longer exist'
                context['error_code'] = 'non-existing'
            return HttpResponse(json.dumps(context))

        @method_decorator(csrf_exempt)
        def dispatch(self, *args, **kwargs):
            return super(ChatView.ChangeChatRequestStatus,
                                self).dispatch(*args, **kwargs)

    class CheckRequestStatus(View):
        """
        Disciple check chat request status
        """

        def post(self, request, *args, **kwargs):
            context = {
                'error': False,
            }
            user_id = request.POST.get('user_id')
            request_code = request.POST.get('request_code')
            try:
                query = Q(user__id=user_id)
                query.add(Q(request_code=request_code), Q.AND)
                chat_request = ChatRequest.objects.get(query)
                context['message'] = ''
                context['status'] = chat_request.get_status_display()
                context['status_code'] = chat_request.status
            except ChatRequest.DoesNotExist:
                context['error'] = True
                context['message'] = 'Request does not exist'
            return HttpResponse(json.dumps(context))

        @method_decorator(csrf_exempt)
        def dispatch(self, *args, **kwargs):
            return super(ChatView.CheckRequestStatus, 
                                self).dispatch(*args, **kwargs)



    class CheckRequestNotifications(View):
        """
        Master check request notifications
        """

        def post(self, request, *args, **kwargs):
            context = {
                'error': False,
            }
            user_id = request.POST.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                query = Q(master=user)
                query.add(Q(status=Notification.STATUS_PENDING), Q.AND)
                query.add(Q(chat_request__status=ChatRequest.STATUS_PENDING), 
                                Q.AND)
                notifications = Notification.objects.filter(query) \
                                    .order_by('created')
                if len(notifications):
                    # send notifications
                    notification_list = []
                    for notification in notifications:
                        notification_list.append({
                            'request_code': notification.chat_request.request_code,
                            'user': notification.chat_request.user.username,
                        })
                        notification.status = Notification.STATUS_SENT
                        notification.save()
                    context['notification_list'] = notification_list;
                    context['message'] = 'Requests available'
                else:
                    context['error'] = False
                    context['notification_list'] = []
                    context['message'] = 'No available requests'
            except User.DoesNotExist:
                context['error'] = True
                context['message'] = 'User does not exist'
            return HttpResponse(json.dumps(context))


        @method_decorator(csrf_exempt)
        def dispatch(self, *args, **kwargs):
            return super(ChatView.CheckRequestNotifications, 
                                self).dispatch(*args, **kwargs)


    class NewMessage(View):
        """
        All user types send message
        """
        def post(self, request, *args, **kwargs):
            context = {
                'error': False,
            }
            request_code = request.POST.get('request_code')
            user_id = request.POST.get('user_id')
            message = request.POST.get('message')
            try:
                user = User.objects.get(id=user_id)
                query = Q(request_code=request_code)
                query.add(Q(status=ChatRequest.STATUS_ACCEPTED), Q.AND)
                chat_request = ChatRequest.objects.get(query)
                chat_message = ChatMessage()
                chat_message.chat_request = chat_request
                chat_message.sender = user
                chat_message.message = message
                chat_message.save()
                msg = '%s: %s' % (user.username, message)
                context['chat_message'] = msg
            except User.DoesNotExist:
                context['error'] = True
                context['message'] = 'User does not exist'
            except ChatRequest.DoesNotExist:
                context['error'] = True
                context['message'] = 'Chat request does not exist'
            return HttpResponse(json.dumps(context))


        @method_decorator(csrf_exempt)
        def dispatch(self, *args, **kwargs):
            return super(ChatView.NewMessage, 
                                self).dispatch(*args, **kwargs)


    class CheckNewMessage(View):
        """
        All user types get new messages
        """
        def post(self, request, *args, **kwargs):
            context = {
                'error': False,
            }            
            existing_ids = request.POST.getlist('existing_ids', [])
            existing_ids = json.loads(existing_ids[0])
            request_code = request.POST.get('request_code')
            try:
                query = Q(request_code=request_code)
                query.add(Q(status=ChatRequest.STATUS_ACCEPTED), Q.AND)
                chat_request = ChatRequest.objects.get(query)
                # filter messages
                message_query = Q(chat_request=chat_request)
                message_query.add(~Q(id__in=existing_ids), Q.AND)
                chat_messages = ChatMessage.objects.filter(message_query) \
                                    .order_by('created')
                new_messages = []
                for message in chat_messages:
                    d = {
                        'id': str(message.id),
                        'message': str(message.message or ''),
                        'sender': str(message.sender.username),
                    }
                    new_messages.append(d)
                context['new_messages'] = new_messages
            except ChatRequest.DoesNotExist:
                context['error'] = True
                context['error_code'] = 'non-existing'
                context['message'] = 'Chat request does not exist'
            return HttpResponse(json.dumps(context))


        @method_decorator(csrf_exempt)
        def dispatch(self, *args, **kwargs):
            return super(ChatView.CheckNewMessage, 
                                self).dispatch(*args, **kwargs)

