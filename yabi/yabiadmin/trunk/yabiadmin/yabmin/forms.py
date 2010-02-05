from django import forms
from django.conf import settings
from yabiadmin.yabmin.models import *


class BackendForm(forms.ModelForm):
    class Meta:
        model = Backend

    def clean_scheme(self):
        scheme = self.cleaned_data['scheme']
        if scheme not in settings.VALID_SCHEMES:
            raise forms.ValidationError("Scheme not valid. Options: %s" % ",".join(settings.VALID_SCHEMES))
        return scheme

    def clean_hostname(self):
        hostname = self.cleaned_data['hostname']
        if hostname.endswith('/'):
            raise forms.ValidationError("Hostname should not end with a /.")
        return hostname

    def clean_path(self):
        path = self.cleaned_data['path']
        if not path.startswith('/'):
            raise forms.ValidationError("Path should start with a /.")
        if not path.endswith('/'):
            raise forms.ValidationError("Path should end with a /.")            
        return path


class BackendCredentialForm(forms.ModelForm):
    class Meta:
        model = BackendCredential

    def clean_homedir(self):
        homedir = self.cleaned_data['homedir']
        if homedir.startswith('/'):
            raise forms.ValidationError("Homedir should not start with a /.")
        if not homedir.endswith('/'):
            raise forms.ValidationError("Homedir should end with a /.")
        return homedir
