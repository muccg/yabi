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
import inspect, itertools, sys

def getinfo(func):
    """Return an info dictionary containing:
    - name (the name of the function : str)
    - argnames (the names of the arguments : list)
    - defarg (the values of the default arguments : list)
    - fullsign (the full signature : str)
    - shortsign (the short signature : str)
    - arg0 ... argn (shortcuts for the names of the arguments)

    >>> def f(self, x=1, y=2, *args, **kw): pass

    >>> info = getinfo(f)

    >>> info["name"]
    'f'
    >>> info["argnames"]
    ['self', 'x', 'y', 'args', 'kw']
    
    >>> info["defarg"]
    (1, 2)

    >>> info["shortsign"]
    'self, x, y, *args, **kw'
    
    >>> info["fullsign"]
    'self, x=defarg[0], y=defarg[1], *args, **kw'

    >>> info["arg0"], info["arg1"], info["arg2"], info["arg3"], info["arg4"]
    ('self', 'x', 'y', 'args', 'kw')
    """
    assert inspect.ismethod(func) or inspect.isfunction(func)
    regargs, varargs, varkwargs, defaults = inspect.getargspec(func)
    argnames = list(regargs)
    if varargs: argnames.append(varargs)
    if varkwargs: argnames.append(varkwargs)
    counter = itertools.count()
    fullsign = inspect.formatargspec(
        regargs, varargs, varkwargs, defaults,
        formatvalue=lambda value: "=defarg[%i]" % counter.next())[1:-1]
    shortsign = inspect.formatargspec(
        regargs, varargs, varkwargs, defaults,
        formatvalue=lambda value: "")[1:-1]
    dic = dict([("arg%s" % n, name) for n, name in enumerate(argnames)])
    dic.update(name=func.__name__, argnames=argnames, shortsign=shortsign,
        fullsign = fullsign, defarg = func.func_defaults or ())
    return dic

def _contains_reserved_names(dic): # helper
    return "_call_" in dic or "_func_" in dic

def _decorate(func, caller, infodict=None):
    """Takes a function and a caller and returns the function
    decorated with that caller. The decorated function is obtained
    by evaluating a function with the correct signature.
    """
    infodict = infodict or getinfo(func)
    assert not _contains_reserved_names(infodict["argnames"]), \
           "You cannot use _call_ or _func_ as argument names!"
    execdict= dict(_func_=func, _call_=caller, defarg=infodict["defarg"])
    if infodict['name'] == "<lambda>":
        lambda_src = "lambda %(fullsign)s: _call_(_func_, %(shortsign)s)" \
                     % infodict
        dec_func = eval(lambda_src, execdict)
    else:
        func_src = """def %(name)s(%(fullsign)s):
        return _call_(_func_, %(shortsign)s)""" % infodict
        # import sys; print >> sys.stderr, func_src # for debugging 
        exec func_src in execdict 
        dec_func = execdict[infodict['name']]
    dec_func.__doc__ = func.__doc__
    dec_func.__dict__ = func.__dict__
    dec_func.__module__ = func.__module__
    return dec_func

class decorator(object):
    """General purpose decorator factory: takes a caller function as
input and returns a decorator. A caller function is any function like this::

    def caller(func, *args, **kw):
        # do something
        return func(*args, **kw)
    
Here is an example of usage:

    >>> @decorator
    ... def chatty(f, *args, **kw):
    ...     print "Calling %r" % f.__name__
    ...     return f(*args, **kw)
    
    >>> @chatty
    ... def f(): pass
    ...
    >>> f()
    Calling 'f'
    """
    def __init__(self, caller):
        self.caller = caller
    def __call__(self, func):
        if sys.version < '2.4': # gracefull fallback
            return lambda *args, **kw : self.caller(func, *args, **kw)
        else:
            return _decorate(func, self.caller)

def newfunc(func, model=None): # not used internally
    """Creates an independent copy of a function. If model is not None,
    the new function copies the signature, as well the attributes
    __name__, __doc__, __dict__ and __module__ from the model, which
    must be a compatible function. Here is an example of usage:
    
    >>> def f(*args, **kw):
    ...     return args[0]*2

    >>> def double(x):
    ...     pass

    >>> help(change_signature(f, double))
    Help on function double in module __main__:
    <BLANKLINE>
    double(x)
    <BLANKLINE>    
    """
    if model is None:
        return new.function(func.func_code, func.func_globals, func.func_name,
                            func.func_defaults, func.func_closure)
    else:
        return _decorate(func, lambda f, *a, **kw : f(*a,**kw),
                         getinfo(model))

##
## Begin
##



@decorator
def tracing(f, *args, **kw):
    print "calling %s with args %s, %s" % (f.func_name, args, kw)
    return f(*args, **kw)
 
def class_annotate(class_declaration):
    for key in class_declaration.__dict__:
        if callable(getattr(class_declaration,key)):
            setattr(class_declaration,key,tracing( getattr(class_declaration,key) ) )
    return class_declaration
 