from django import forms
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _


class LoginForm(forms.Form):

    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        return self.cleaned_data
