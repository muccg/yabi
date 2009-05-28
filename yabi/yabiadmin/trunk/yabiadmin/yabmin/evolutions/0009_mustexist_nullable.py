from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    ChangeField('ToolOutputExtension', 'must_exist', initial=None, null=True)
]
