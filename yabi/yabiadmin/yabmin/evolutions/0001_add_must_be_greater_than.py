from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('ToolOutputExtension', 'must_be_greater_than', models.PositiveIntegerField, null=True)
]
