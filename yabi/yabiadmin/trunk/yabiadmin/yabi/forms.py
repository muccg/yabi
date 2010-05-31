from django import forms
from django.conf import settings
from yabiadmin.yabi.models import *


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
            raise forms.ValidationError("Hostname must not end with a /.")
        return hostname

    def clean_path(self):
        path = self.cleaned_data['path']
        if not path.startswith('/'):
            raise forms.ValidationError("Path must start with a /.")
        if not path.endswith('/'):
            raise forms.ValidationError("Path must end with a /.")            
        return path


class BackendCredentialForm(forms.ModelForm):
    class Meta:
        model = BackendCredential

    def clean_homedir(self):
        homedir = self.cleaned_data['homedir']
        if homedir:
            if homedir.startswith('/'):
                raise forms.ValidationError("Homedir must not start with a /.")
            if not homedir.endswith('/'):
                raise forms.ValidationError("Homedir must end with a /.")
        return homedir

    def clean_default_stageout(self):

        default_stageout = self.cleaned_data['default_stageout']

        if default_stageout:
            stageout_count = 0
            becs = BackendCredential.objects.filter(credential__user=self.cleaned_data['credential'].user)

            for bec in becs:
                 # check for other credentials that have stageout on,
                 # but don't include the one user is editing
                if bec.default_stageout and bec != self.instance:
                    stageout_count += 1

            if stageout_count > 0:
                raise forms.ValidationError("There is a backend credential flagged as the default stageout already.")
            
        return default_stageout


class ToolForm(forms.ModelForm):
    class Meta:
        model = Tool
        exclude = ('groups','output_filetypes')

    def __init__(self, *args, **kwargs):
        super(ToolForm, self).__init__(*args, **kwargs)
        self.fields["batch_on_param"].queryset = ToolParameter.objects.filter(tool=self.instance)

    def clean_backend(self):
        backend = self.cleaned_data['backend']
        if backend.path != '/':
            raise forms.ValidationError("Execution backends must only have / in the path field. (This is probably a file system backend.)")
        return backend

