from typing import Optional

from manager.models import Package, Build


def get_latest_build(package: Package) -> Optional[Build]:
    try:
        return Build.objects.filter(package=package, status=Build.SUCCESS).order_by('-id')[0]
    except IndexError:
        return None
