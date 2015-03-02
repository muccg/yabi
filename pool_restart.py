import celery
from yabiadmin.backend.celerytasks import app

app.control.broadcast('pool_restart')
