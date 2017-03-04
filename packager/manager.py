import json
import queue
import threading
import time

import django.utils.timezone as timezone

import lib.digest as digest
import packager.local_repository
import packager.path
import packager.slack
from lib.singleton import Singleton
from manager.models import Build, Artifact
from packager.builder import Builder, BuilderError
from packager.settings import SLACK_NOTIFICATION, CUSTOM_LOCAL_REPOSITORY


class BuilderManager(metaclass=Singleton):
    def __init__(self):
        self.build_queue = queue.Queue()
        self.lock = threading.Lock()
        self.building_packages = set()
        self.builder_thread = threading.Thread(target=self._builder_main)
        self.builder_thread.start()

    def register(self, package_id):
        self.build_queue.put(package_id)

    def _build(self, package_id):
        builder = Builder(package_id)
        if builder.package_name in self.building_packages:
            # TODO: Error handling: duplicate package build
            pass
        else:
            with self.lock:
                self.building_packages.add(builder.package_name)
            date = timezone.now()
            build = Build(package=builder.package, status=Build.BUILDING, date=date)
            build.save()
            try:
                builder.build(date)
            except (BuilderError, PermissionError):
                build.status = Build.FAILURE
            finally:
                build.version = builder.version
            if not build.status == build.FAILURE:
                try:
                    path = packager.path.build_to_path(build)
                    d = {}
                    for pkgname in Artifact.objects.filter(package=build.package):
                        d[pkgname.name] = digest.sha256(path.artifact_file(pkgname.name))
                    build.status = Build.SUCCESS
                    build.sha256 = json.dumps(d)
                except FileNotFoundError:
                    build.status = Build.FAILURE
            build.save()
            if SLACK_NOTIFICATION:
                packager.slack.post(build)
            if CUSTOM_LOCAL_REPOSITORY:
                packager.local_repository.update_repository(build)

            with self.lock:
                self.building_packages.remove(builder.package_name)

    def _builder_main(self):
        while True:
            try:
                package_id = self.build_queue.get()
            except queue.Empty:
                time.sleep(1)
            else:
                worker = threading.Thread(target=self._build, args=(package_id,))
                worker.start()
