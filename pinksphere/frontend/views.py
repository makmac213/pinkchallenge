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

# frontend
from .forms import LoginForm

class FrontendView(object):

    class Index(TemplateView):
        template_name = 'frontend/landing.html'


    class Login(View):

        def post(self, request, *args, **kwargs):
            logout(request)

            form = LoginForm(request.POST)

            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                auth_user = authenticate(username=username, password=password)
                if auth_user is not None:
                    if auth_user.is_active:
                        login(request, auth_user)
                        # chech user type
                        msg = 'Logged-in'
                    else:
                        # user is inactive
                        msg = 'User inactive'
                else:
                    # user does not exist
                    msg = 'User does not exist`'
            else:
                msg = get_form_error_messages(form)

            return HttpResponse(msg)


    class Logout(View):
        def get(self, request, *args, **kwargs):
            logout(request)
            return redirect('index') 

