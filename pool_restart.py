import celery
from yabi.backend.celerytasks import app

app.control.broadcast('pool_restart')
