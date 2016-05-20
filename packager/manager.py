from packager.builder import Builder
import threading
import queue
import time
from misc.singleton import Singleton
from manager.models import Build
import django.utils.timezone as timezone


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
                result_path, log_path, version = builder.build(date)
            except:
                build.status = Build.FAILURE
                raise
            else:
                build.version = version
                build.date = date
                build.result_path = result_path
                build.log_path = log_path
                build.status = Build.SUCCESS
            build.save(force_update=True)
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
