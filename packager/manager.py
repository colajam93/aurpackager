from packager.builder import Builder
import multiprocessing
import queue
import time
from misc.singleton import Singleton


class BuilderManager(metaclass=Singleton):
    def __init__(self):
        self.build_queue = multiprocessing.Queue()
        self.building_packages = []
        self.build_process = multiprocessing.Process(target=self._builder_main)
        self.build_process.start()

    def register(self, package_id):
        self.build_queue.put(package_id)

    def complete(self, package_id):
        pass

    def _builder_main(self):
        while True:
            try:
                package_id = self.build_queue.get()
            except queue.Empty:
                time.sleep(1)
            else:
                builder = Builder(package_id)
                if builder.package_name in self.building_packages:
                    # TODO: Error handling: duplicate package build
                    pass
                else:
                    self.building_packages.append(builder.package_name)
                    builder.build()
