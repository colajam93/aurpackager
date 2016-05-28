from manager.models import Package
import lib.aur.query as query
import lib.pacman.sync as sync
import itertools


class OperationError(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return repr(self.reason)


def register(name):
    info = query.info(name)
    native = []
    foreign = []
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
        register(package)

    package = Package(name=name)
    package.save()
