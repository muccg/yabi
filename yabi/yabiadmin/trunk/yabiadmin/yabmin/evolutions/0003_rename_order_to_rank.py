from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('ToolRslArgumentOrder', 'rank', models.PositiveIntegerField, null=True),
    DeleteField('ToolRslArgumentOrder', 'order')
]
