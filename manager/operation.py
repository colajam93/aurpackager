from manager.models import Package
import lib.aur.query as query
import lib.pacman.sync as sync
import itertools


class OperationError(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return repr(self.reason)


def __is_registered(name):
    try:
        Package.objects.get(name=name)
    except Package.DoesNotExist:
        return False
    else:
        return True


def register(name, with_depend=False):
    if __is_registered(name):
        raise OperationError('{} has already installed'.format(name))

    info = query.info(name)
    native = []
    foreign = []
    if with_depend:
        depends = []
        if hasattr(info, 'Depends'):
            depends.append(info.Depends)
        if hasattr(info, 'MakeDepends'):
            depends.append(info.MakeDepends)
        for depend in itertools.chain(*depends):
            depend_name = depend.translate(str.maketrans('>=', '<<')).split('<')[0]
            if sync.exist(depend_name):
                native.append(depend_name)
            elif query.exist(depend_name):
                foreign.append(depend_name)
            else:
                raise OperationError('{} not found'.format(depend_name))
        sync.install(native, asdeps=True)
        for package in foreign:
            if not __is_registered(package):
                r = register(package, with_depend=True)
                native.extend(r['native'])
                foreign.extend(r['foreign'])

    package = Package(name=name)
    package.save()
    ret = dict()
    ret['native'] = list(set(native))
    ret['foreign'] = list(set(foreign))
    return ret
