from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('ToolParameter', 'filter_value', models.CharField, max_length=50, null=True),
    DeleteField('ToolParameter', 'filterValue')
]
