from django import forms

from yabife.yabifeapp.models import Appliance


class RegistrationForm(forms.Form):
    appliance = forms.ModelChoiceField(queryset=Appliance.objects.all())
    username = forms.CharField(max_length=30)
    email = forms.EmailField(label="E-mail address")
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    def add_error(self, name, message):
        if name in self.errors:
            self.errors[name].append(message)
        else:
            self.errors[name] = [message]

    def add_global_error(self, message):
        self.add_error(forms.forms.NON_FIELD_ERRORS, message)
