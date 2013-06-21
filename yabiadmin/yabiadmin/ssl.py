# -*- coding: utf-8 -*-
__license__ = "Python"
__copyright__ = "Copyright (C) 2007, Stephen Zabel"
__author__ = "Stephen Zabel - sjzabel@gmail.com"
__contributors__ = "Jay Parlar - parlar@gmail.com"

# CCG modification for get_hostname Django 1.5.1

from django.conf import settings
#from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect, get_host

from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
SSL = 'SSL'

class SSLRedirect:
    def process_request(self, request):
        ssl_force = getattr(settings, 'SSL_FORCE', None)
        if settings.SSL_ENABLED and ssl_force:
            if not self._is_secure(request):
                return self._redirect(request, True)
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        if SSL in view_kwargs:
            secure = view_kwargs[SSL]
            del view_kwargs[SSL]
        else:
            # none means I don't care if its secure or not, just let the request through
            return None

        if (not secure == self._is_secure(request)) and settings.SSL_ENABLED:
            return self._redirect(request, secure)

    def _is_secure(self, request):
        if request.is_secure():
            return True

        #Handle the Webfaction case until this gets resolved in the request.is_secure()
        if 'HTTP_X_FORWARDED_SSL' in request.META:
            return request.META['HTTP_X_FORWARDED_SSL'] == 'on'

        return False

    def _redirect(self, request, secure):
        protocol = secure and "https" or "http"
        host = request.get_host()

        # if we are being proxied use the default behavoir. Thus proxied servers will only work if outside the proxy they look like they are on standard ports.
        if 'HTTP_X_FORWARDED_HOST' not in request.META:
            if hasattr(settings,'HTTP_REDIRECT_TO_HTTPS'):
                host = settings.HTTP_REDIRECT_TO_HTTPS

            if hasattr(settings,'HTTP_REDIRECT_TO_HTTPS_PORT'):
                host = host.split(":")[0] + ":" + str(settings.HTTP_REDIRECT_TO_HTTPS_PORT)

        newurl = "%s://%s%s" % (protocol,host,request.get_full_path())
        if settings.DEBUG and request.method == 'POST':
            raise RuntimeError, \
        """Django can't perform a SSL redirect while maintaining POST data.
           Please structure your views so that redirects only occur during GETs."""

        return HttpResponsePermanentRedirect(newurl)
