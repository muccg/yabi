from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('ToolRslArgumentOrder', 'order', models.PositiveIntegerField, initial=0),
    DeleteField('ToolRslArgumentOrder', 'rank'),
]
