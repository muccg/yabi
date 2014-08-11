# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics
# (http://ccg.murdoch.edu.au/).
#
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS,"
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS.
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
#
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
from django import forms
from django.utils import simplejson as json
from yabiadmin.yabi.models import *
from yabiadmin.crypto_utils import any_unencrypted, any_annotated_block
from django.core.exceptions import ValidationError


def get_backend_caps():
    from ..backend import BaseBackend
    return BaseBackend.get_caps()


class CapsField(forms.CharField):
    def __init__(self):
        super(CapsField, self).__init__(required=False,
                                        widget=forms.HiddenInput,
                                        initial=json.dumps(get_backend_caps()))


class BackendForm(forms.ModelForm):
    caps = CapsField()

    class Meta:
        model = Backend

    def clean(self):
        cleaned_data = super(BackendForm, self).clean()
        dynamic_backend = cleaned_data.get("dynamic_backend")
        dynamic_backend_configuration = cleaned_data.get("dynamic_backend_configuration")

        if dynamic_backend and dynamic_backend_configuration is None:
            raise forms.ValidationError("You must select a Dynamic Backend Configuration "
                                        "for a Dynamic Backend.")
        scheme = self.cleaned_data.get('scheme')

        caps = get_backend_caps()

        if scheme in caps:
            for attr, name in (("lcopy_supported", "Local Copy"), ("link_supported", "Linking")):
                if self.cleaned_data.get(attr) and not caps[scheme].get(attr, False):
                    self._errors[attr] = self.error_class(["%s not supported on %s." % (name, scheme)])
                    del cleaned_data[attr]
        elif not scheme:
            self._errors["scheme"] = self.error_class(["This field is required."])
        else:
            msg = "Scheme not valid. Options: " + ", ".join(sorted(caps))
            self._errors["scheme"] = self.error_class([msg])
            del cleaned_data["scheme"]

        return cleaned_data

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


class CredentialForm(forms.ModelForm):
    auth_class = forms.ChoiceField(label="Type", required=False)
    caps = CapsField()

    class Meta:
        model = Credential

    def clean(self):
        cleaned_data = super(CredentialForm, self).clean()

        # fields to which security_state applies, or from which it can be inferred
        crypto_fields = ('password', 'key')
        crypto_values = [cleaned_data.get(t) for t in crypto_fields]

        # are any of the crypto_fields set to a non-empty, non-annotated-block value?
        have_unencrypted_field = any_unencrypted(*crypto_values)
        # are any of the crypto_fields set to a non-empty, annotated-block value?
        have_annotated_field = any_annotated_block(*crypto_values)

        if have_unencrypted_field and have_annotated_field:
            raise forms.ValidationError("Submitted form contains some plain text data and some encrypted data. If you wish to update credentials, you must update all fields.")

        return cleaned_data


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
        exclude = ('use_same_dynamic_backend',)

    def clean_backend(self):
        backend = self.cleaned_data['backend']
        if backend.path != '/':
            raise forms.ValidationError("Execution backends must only have / in the path field. (This is probably a file system backend.)")
        return backend


class ToolParameterForm(forms.ModelForm):
    class Meta:
        model = ToolParameter

    def __init__(self, *args, **kwargs):
        super(ToolParameterForm, self).__init__(*args, **kwargs)

        if self.instance:
            # removes this tool parameter as an option for use_output_filename
            field = self.fields["use_output_filename"]
            field.queryset = field.queryset.exclude(id__exact=self.instance.id)

    def clean_possible_values(self):
        validator = _compose(_validate_json, _wspace_to_empty)
        return validator(self.cleaned_data['possible_values'])


class ToolOutputExtensionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ToolOutputExtensionForm, self).__init__(*args, **kwargs)
        self.fields['file_extension'].queryset = FileExtension.objects.all().order_by('pattern')


class DynamicBackendConfigurationForm(forms.ModelForm):
    class Meta:
        model = DynamicBackendConfiguration

    def clean_configuration(self):
        validator = _compose(_validate_json, _wspace_to_empty)
        return validator(self.cleaned_data['configuration'])


def _compose(*funcs):
    return reduce(lambda f, g: lambda x: f(g(x)), funcs)


def _wspace_to_empty(value):
    if value.strip() == '':
        return ''
    return value


def _validate_json(value):
    if value == '':
        return ''
    try:
        json.loads(value)
    except ValueError:
        raise ValidationError('Invalid JSON.')
    return value
