from collections import deque
from packager.builder import Builder


class BuilderManager:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if BuilderManager.__instance is None:
            BuilderManager.__instance = object.__new__(cls)
        return BuilderManager.__instance

    def __init__(self):
        self.build_queue = deque()

    def register(self, package_id):
        build = Builder(package_id)
        self.build_queue.append(build)
