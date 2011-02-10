# -*- coding: utf-8 -*-


def check_database(request):
    """
    Check that we can communicate with the Frontend database by checking that
    both the appliance and user models have at least one record defined. (If
    they don't, we really have bigger problems.
    """

    from yabifeapp.models import Appliance, User

    return (Appliance.objects.count() > 1 and User.objects.count() > 1)


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
