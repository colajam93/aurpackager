import enum
import itertools
import os.path
import shutil

from typing import Dict, List

import lib.aur as aur
import lib.pacman.sync as sync
import lib.pacman.upgrade as upgrade
import packager.path
from manager.models import Package, Build, Artifact
from packager.manager import BuilderManager
from packager.path import build_to_path
from packager.settings import BUILD_ROOT_DIR


class OperationError(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return repr(self.reason)


class RegisterStatus(enum.Enum):
    package = 1
    artifact = 2
    not_registered = 3


def _is_registered(name: str) -> bool:
    return not _register_status(name)[0] == RegisterStatus.not_registered


def _register_status(name: str) -> (RegisterStatus, str):
    if Package.objects.filter(name=name).exists():
        return RegisterStatus.package, name
    else:
        a = Artifact.objects.filter(name=name)
        if a.exists():
            return RegisterStatus.artifact, a[0].package.name
        else:
            return RegisterStatus.not_registered, ''


# TODO: Refactor too naive implementation
def register(name: str, server: str, with_depend: bool = False) -> Dict[str, List[str]]:
    (is_registered, registered_name) = _register_status(name)
    if is_registered == RegisterStatus.package:
        raise OperationError('{} has already registered'.format(name))
    elif is_registered == RegisterStatus.artifact:
        raise OperationError('{} has already registered as Artifact of {}'.format(name, registered_name))

    info = aur.detail_info(name, server)
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
            elif aur.exist(depend_name, Package.OFFICIAL):
                foreign.append(depend_name)
            else:
                raise OperationError('{} not found'.format(depend_name))
        sync.system_upgrade()
        sync.install(native, asdeps=True)
        for package in foreign:
            if not _is_registered(package):
                # Dependent package will register from official server
                r = register(package, Package.OFFICIAL, with_depend=True)
                native.extend(r['native'])
                foreign.extend(r['foreign'])

    for duplicate in (set(foreign) & set(info.pkgnames)):
        d = Package.objects.filter(name=duplicate)
        if d.exists():
            d.delete()
    package = Package(name=name, server=server)
    package.save()
    for pkgname in info.pkgnames:
        artifact = Artifact(package=package, name=pkgname)
        artifact.save()
    ret = dict()
    ret['native'] = list(set(native))
    ret['foreign'] = list(set(foreign))
    return ret


def remove_package(name, cleanup=False):
    if not _is_registered(name):
        raise OperationError('{} has not registered'.format(name))

    if cleanup:
        shutil.rmtree(os.path.join(BUILD_ROOT_DIR, name), ignore_errors=True)

    package = Package.objects.get(name=name)
    package.delete()


def _remove_build(build_: Build) -> None:
    path = build_to_path(build_)
    shutil.rmtree(path.build_dir, ignore_errors=True)
    build_.delete()


def remove_build(name: str, build_number: int) -> None:
    if not _is_registered(name):
        raise OperationError('{} has not registered'.format(name))
    try:
        build_ = Build.objects.filter(package__name=name).order_by('-id')[build_number - 1]
        _remove_build(build_)
    except IndexError:
        raise OperationError('{} build {} is not existed'.format(name, build_number))


def cleanup(name: str) -> None:
    if not _is_registered(name):
        raise OperationError('{} has not registered'.format(name))
    for build_ in Build.objects.filter(package__name=name, status=Build.FAILURE):
        _remove_build(build_)
    try:
        for build_ in Build.objects.filter(package__name=name, status=Build.SUCCESS).order_by('-id')[1:]:
            _remove_build(build_)
    except IndexError:
        pass


def cleanup_all() -> None:
    for package in Package.objects.all():
        cleanup(package.name)


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
    # dict of server tag to list of Build
    need_check: Dict[str, List[Build]] = {}
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
                if latest.package.server in need_check:
                    need_check[latest.package.server].append(latest)
                else:
                    need_check[latest.package.server] = [latest]
    if need_check:
        for k, v in need_check.items():
            multiple_info_ = aur.multiple_info([x.package.name for x in v], k)
            for p in v:
                package_name = p.package.name
                if multiple_info_[package_name] and multiple_info_[package_name].Version != p.version:
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
            completed = upgrade.install(path.artifact_file(name))
            if completed.returncode:
                raise OperationError(
                    'stdout:\n{}\n\nstderr\n:{}'.format(completed.stdout.decode(), completed.stderr.decode()))
        except FileNotFoundError as e:
            raise OperationError from e
    else:
        raise OperationError('{} latest build has not succeeded'.format(name))


def toggle_ignore(name):
    if not _is_registered(name):
        raise OperationError('{} has not registered'.format(name))

    package = Package.objects.get(name=name)
    package.ignore = not package.ignore
    package.save()
    return package.ignore
