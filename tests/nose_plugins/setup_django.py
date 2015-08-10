from nose.plugins import Plugin

class SetupDjango(Plugin):
    name = 'setup-django'
    enabled = True

    def configure(self, options, conf):
        pass

    def begin(self):
        import django
        django.setup()
