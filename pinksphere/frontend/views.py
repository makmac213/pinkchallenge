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

# common
from common.utils import get_form_error_messages

# chat
from chat.models import MasterAvailability, ChatRequest

# frontend
from .forms import LoginForm


class FrontendView(object):

    class Index(View):
        template_name = 'frontend/landing.html'

        def get(self, request, *args, **kwargs):
            current_request_code = None
            current_request_status = None

            if request.user.is_authenticated():
                if request.user.groups.filter(id=settings.MEMBER_DISCIPLE).count():
                    # get latest accepted chat
                    accepted_query = Q(user=request.user)
                    accepted_query.add(Q(status=ChatRequest.STATUS_ACCEPTED), Q.AND)
                    chat_requests = ChatRequest.objects.filter(accepted_query)
                    if len(chat_requests):
                        current_request_code = chat_requests[0].request_code
                        current_request_status = chat_requests[0].status
                    else:
                        # get latest pending chat request
                        pending_query = Q(user=request.user)
                        pending_query.add(Q(status=ChatRequest.STATUS_PENDING), Q.AND)
                        chat_requests = ChatRequest.objects.filter(pending_query)
                        if len(chat_requests):
                            current_request_code = chat_requests[0].request_code
                            current_request_status = chat_requests[0].status
                elif request.user.groups.filter(id=settings.MEMBER_MASTER).count():
                    pass
            context = {
                'current_request_code': current_request_code,
                'current_request_status': current_request_status,
            }
            return render(request, self.template_name, context)

    class Login(View):

        def post(self, request, *args, **kwargs):
            logout(request)

            ret = request.GET.get('next', 'index')

            form = LoginForm(request.POST)

            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                auth_user = authenticate(username=username, password=password)
                if auth_user is not None:
                    if auth_user.is_active:
                        login(request, auth_user)
                        # check user type member/disciple
                        if auth_user.groups.filter(id=settings.MEMBER_MASTER).count():
                            # user is a master create availability
                            # delete previous record
                            existing = MasterAvailability.objects.filter(user=auth_user)
                            for availability in existing:
                                availability.delete()
                            # create record
                            availability = MasterAvailability()
                            availability.user = auth_user
                            availability.save()

                        elif auth_user.groups.filter(id=settings.MEMBER_DISCIPLE).count():
                            # add other disciple functionalities here
                            pass                            
                        messages.success(request, 'Welcome')
                        print 1
                    else:
                        # user is inactive
                        print 2
                        messages.error(request, 'Invalid username/password')
                else:
                    # user does not exist
                    print 3
                    messages.error(request, 'Invalid username/password')

            else:
                print 4
                msg = get_form_error_messages(form)
                messages.error(request, msg)
            return redirect(ret)


    class Logout(View):
        def get(self, request, *args, **kwargs):
            user = request.user
            if user.groups.filter(id=settings.MEMBER_MASTER).count():
                # delete availabilities
                existing = MasterAvailability.objects.filter(user=user)
                for availability in existing:
                    availability.delete()
            elif user.groups.filter(id=settings.MEMBER_DISCIPLE).count():
                # end all pending and accepted chat
                # accepted
                query = Q(user=request.user)
                sub_query = Q(status=ChatRequest.STATUS_ACCEPTED)
                sub_query.add(Q(status=ChatRequest.STATUS_PENDING), Q.OR)
                query.add(sub_query, Q.AND)
                chat_requests = ChatRequest.objects.filter(query)
                for chat_request in chat_requests:
                    chat_request.status = ChatRequest.STATUS_ENDED
                    chat_request.save()

            logout(request)
            return redirect('index') 

