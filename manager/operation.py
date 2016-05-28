from manager.models import Package


class OperationError(Exception):
    pass


def register(name):
    package = Package(name=name)
    package.save()
