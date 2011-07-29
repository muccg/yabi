# -*- coding: utf-8 -*-
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
# -*- coding: utf-8 -*-


def check_database(request):
    """
    Check that we can communicate with the Frontend database by checking that
    both the appliance and user models have at least one record defined. (If
    they don't, we really have bigger problems.
    """

    from yabifeapp.models import Appliance, User

    return (Appliance.objects.count() > 0 and User.objects.count() > 1)


def check_disk(request):
    """
    Attempt to write something to the server's disk to test for a disk full
    error. This is an extremely naïve check that doesn't try to enumerate
    partitions, or even ensure that it's writing to the same partition Django
    would be using for its own purposes, but really, that's preserve of
    something like Nagios and NRPE: this is merely a simple sanity check.
    """

    from tempfile import NamedTemporaryFile

    # I'm using NamedTemporaryFile instead of TemporaryFile just in case
    # there's a file system that's smart enough to not actually write to disk
    # for a file that doesn't have a real link to the file system (as Python
    # attempts to do for TemporaryFile).
    with NamedTemporaryFile() as fp:
        fp.write("It really doesn't matter what we write here")
        fp.flush()

    # If we got here without throwing an exception, we're all good.
    return True
