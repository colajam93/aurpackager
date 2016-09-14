from manager.models import Package, Build
import lib.aur as aur
import lib.pacman.sync as sync
import lib.pacman.upgrade as upgrade
import itertools
import shutil
import os.path
from packager.settings import BUILD_ROOT_DIR
from packager.manager import BuilderManager
import packager.path


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
        raise OperationError('{} has already registered'.format(name))

    info = aur.info(name)
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
            elif aur.exist(depend_name):
                foreign.append(depend_name)
            else:
                raise OperationError('{} not found'.format(depend_name))
        sync.system_upgrade()
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
        raise OperationError('{} has not registered'.format(name))

    if cleanup:
        shutil.rmtree(os.path.join(BUILD_ROOT_DIR, name), ignore_errors=True)

    package = Package.objects.get(name=name)
    package.delete()


def build(name):
    if not _is_registered(name):
        raise OperationError('{} has not registered'.format(name))

    package = Package.objects.get(name=name)
    sync.system_upgrade()
    BuilderManager().register(package.id)


def build_all():
    packages = Package.objects.all()
    sync.system_upgrade()
    for package in packages:
        BuilderManager().register(package.id)


def build_update():
    packages = Package.objects.all()
    sync.system_upgrade()
    need_check = list()
    for package in packages:
        if package.ignore:
            continue
        try:
            latest = Build.objects.filter(package_id=package.id).order_by('-id')[0]
        except IndexError:
            BuilderManager().register(package.id)
        else:
            if latest.status == Build.FAILURE:
                BuilderManager().register(package.id)
            elif latest.status == Build.SUCCESS:
                need_check.append(latest)
    if need_check:
        infos = aur.multiple_info(list(map(lambda x: x.package.name, need_check)))
        for p in need_check:
            package_name = p.package.name
            if infos[package_name] and infos[package_name].Version != p.version:
                BuilderManager().register(p.package.id)


def install(name):
    if not _is_registered(name):
        raise OperationError('{} has not registered'.format(name))

    package = Package.objects.get(name=name)
    try:
        build_ = Build.objects.filter(package_id=package.id).order_by('-id')[0]
    except IndexError:
        raise OperationError('{} has no build'.format(name))
    if build_.status == Build.SUCCESS:
        try:
            path = packager.path.build_to_path(build_)
            sync.system_upgrade()
            completed = upgrade.install(path.result_file)
            if completed.returncode:
                raise OperationError(
                    'stdout:\n{}\n\nstderr\n:{}'.format(completed.stdout.decode(), completed.stderr.decode()))
        except FileNotFoundError as e:
            raise OperationError from e
    else:
        raise OperationError('{} latest build has not succeeded'.format(name))


def install_all():
    files = []
    for package in Package.objects.all():
        try:
            latest = Build.objects.filter(package_id=package.id).order_by('-id')[0]
        except IndexError:
            pass
        else:
            if latest.status == Build.SUCCESS:
                try:
                    path = packager.path.build_to_path(latest)
                    files.append(path.result_file)
                except FileNotFoundError:
                    pass
    upgrade.install(' '.join(files))


def toggle_ignore(name):
    if not _is_registered(name):
        raise OperationError('{} has not registered'.format(name))

    package = Package.objects.get(name=name)
    package.ignore = not package.ignore
    package.save()
    return package.ignore
