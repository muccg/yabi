
def run(args):
    args = args.split(",")
    assert len(args) == 2, "Classname and/or method not passed in"
    parts = args[0].split('.')
    modname, classname = ".".join(parts[:-1]), parts[-1]
    methodname = args[1]
    module = __import__(modname, fromlist=['*'])

    cls = getattr(module, classname)

    getattr(cls, methodname)()
