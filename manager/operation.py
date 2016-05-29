from manager.models import Package
import lib.aur.query as query
import lib.pacman.sync as sync
import itertools
import shutil
import os.path
from packager.settings import BUILD_ROOT_DIR
from packager.manager import BuilderManager


class OperationError(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return repr(self.reason)


def _is_registered(name):
    try:
        Package.objects.get(name=name)
    except Package.DoesNotExist:
        return False
    else:
        return True


def register(name, with_depend=False):
    if _is_registered(name):
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
            if not _is_registered(package):
                r = register(package, with_depend=True)
                native.extend(r['native'])
                foreign.extend(r['foreign'])

    package = Package(name=name)
    package.save()
    ret = dict()
    ret['native'] = list(set(native))
    ret['foreign'] = list(set(foreign))
    return ret


def remove(name, cleanup=False):
    if not _is_registered(name):
        raise OperationError('{} has not installed'.format(name))

    if cleanup:
        shutil.rmtree(os.path.join(BUILD_ROOT_DIR, name), ignore_errors=True)

    package = Package.objects.get(name=name)
    package.delete()


def build(name):
    if not _is_registered(name):
        raise OperationError('{} has not installed'.format(name))

    package = Package.objects.get(name=name)
    BuilderManager().register(package.id)


def build_all():
    packages = Package.objects.all()
    for package in packages:
        BuilderManager().register(package.id)
