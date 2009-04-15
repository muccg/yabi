from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    ChangeField('ToolParameter', 'switch', initial=None, unique=False)
]
