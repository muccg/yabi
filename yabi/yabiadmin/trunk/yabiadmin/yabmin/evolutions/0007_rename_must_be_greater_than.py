from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('ToolOutputExtension', 'must_be_larger_than', models.PositiveIntegerField, null=True),
    DeleteField('ToolOutputExtension', 'must_be_greater_than')
]
