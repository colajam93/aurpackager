import os.path
import shutil
import subprocess

from manager.models import Package, Artifact, Build
from manager.utilities import get_latest_build
from packager.path import build_to_path
from packager.settings_local import CUSTOM_LOCAL_REPOSITORY_DIR, CUSTOM_LOCAL_REPOSITORY_NAME

DB_FILENAME = '{}.db.tar.xz'.format(CUSTOM_LOCAL_REPOSITORY_NAME)
DB_PATH = CUSTOM_LOCAL_REPOSITORY_DIR
DB_FILE = os.path.join(DB_PATH, DB_FILENAME)


def _run_repo_add(path: str) -> None:
    subprocess.run(['repo-add', '-q', '-R', '-n', DB_FILE, path], stderr=subprocess.DEVNULL)


def _is_db_initialized() -> bool:
    return os.path.exists(DB_PATH) and os.path.exists(DB_FILE)


def _build_initial_db() -> None:
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH)
    for package in Package.objects.all():
        latest = get_latest_build(package)
        if not latest:
            continue
        _update_package(latest)


def _update_package(build: Build) -> None:
    path = build_to_path(build)
    for artifact in Artifact.objects.filter(package=build.package):
        copied_path = shutil.copy(path.artifact_file(artifact.name), DB_PATH)
        _run_repo_add(copied_path)


def update_repository(build: Build) -> None:
    if not os.path.exists(DB_FILE):
        _build_initial_db()
    else:
        _update_package(build)
