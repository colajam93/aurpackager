from manager.models import Package
import packager.settings
from urllib.request import urlopen
from contextlib import closing
import json

RPC_URL = 'https://aur.archlinux.org/rpc/?v=5&type=info&arg[]={}'


class BuilderError(Exception):
    pass

class Builder:
    def __init__(self, package_id):
        self.package = Package.objects.get(id=package_id)
        with closing(urlopen(RPC_URL.format(self.package.name))) as request:
            self.package_detail = json.loads(request.read().decode())
            print(self.package_detail)
        if not self.package_detail['resultcount'] == 1:
            raise BuilderError
