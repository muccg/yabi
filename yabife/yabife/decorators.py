### BEGIN COPYRIGHT ###
#
# (C) Copyright 2011, Centre for Comparative Genomics, Murdoch University.
# All rights reserved.
#
# This product includes software developed at the Centre for Comparative Genomics 
# (http://ccg.murdoch.edu.au/).
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, YABI IS PROVIDED TO YOU "AS IS," 
# WITHOUT WARRANTY. THERE IS NO WARRANTY FOR YABI, EITHER EXPRESSED OR IMPLIED, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY RIGHTS. 
# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF YABI IS WITH YOU.  SHOULD 
# YABI PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR
# OR CORRECTION.
# 
# TO THE EXTENT PERMITTED BY APPLICABLE LAWS, OR AS OTHERWISE AGREED TO IN 
# WRITING NO COPYRIGHT HOLDER IN YABI, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR 
# REDISTRIBUTE YABI AS PERMITTED IN WRITING, BE LIABLE TO YOU FOR DAMAGES, INCLUDING 
# ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE 
# USE OR INABILITY TO USE YABI (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR 
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES 
# OR A FAILURE OF YABI TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER 
# OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
# 
### END COPYRIGHT ###
from ccg.http import HttpResponseUnauthorized
from yabifeapp.utils import mail_admins_no_profile
from django.core.exceptions import ObjectDoesNotExist

from yabifeapp.utils import mail_admins_no_profile, logout
from yabife.responses import JsonMessageResponseUnauthorized

import logging
logger = logging.getLogger('yabife')

def authentication_required(f):

    def new_function(*args, **kwargs):
        request = args[0]
        if not request.user.is_authenticated():
            return HttpResponseUnauthorized()
        return f(*args, **kwargs)
    return new_function


def profile_required(func):
    def newfunc(request,*args,**kwargs):
        # Check if the user has a profile; if not, nothing's going to work anyway,
        # so we might as well fail more spectacularly.
        try:
            request.user.get_profile()

        except ObjectDoesNotExist:
            mail_admins_no_profile(request.user)
            logger.critical("User does not have a profile: %s" % request.user)
            return logout(request)

        except AttributeError:
            logger.critical("Anonymous user attempting to access Yabi")
            return JsonMessageResponseUnauthorized("Anonymous users do not have access to YABI")

        return func(request, *args, **kwargs)    
            
    return newfunc
