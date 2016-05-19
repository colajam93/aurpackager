from manager.models import Package
from packager.settings import BUILD_ROOT_DIR
from urllib.request import urlopen
from contextlib import closing
import json
import os
import os.path
import datetime
import subprocess

AUR_URL = 'https://aur.archlinux.org'
RPC_URL = AUR_URL + '/rpc/?v=5&type=info&arg[]={}'


class BuilderError(Exception):
    pass


class Builder:
    def __init__(self, package_id):
        package = Package.objects.get(id=package_id)
        with closing(urlopen(RPC_URL.format(package.name))) as request:
            result = json.loads(request.read().decode())
        detail = result['results'][0]
        tar_url = AUR_URL + detail['URLPath']
        date = datetime.datetime.now().isoformat()
        build_dir = os.path.join(BUILD_ROOT_DIR, package.name, detail['Version'], date)
        package_name = detail['Name']
        tar_path = os.path.join(build_dir, package_name)
        os.makedirs(build_dir, 0o700)
        with closing(urlopen(tar_url)) as request:
            with open(tar_path, 'wb') as f:
                f.write(request.read())
        build_script = '''
#!/bin/bash

cd {build_dir}
tar xvf {package_name}
cd {package_name}
makepkg -s
'''
        build_script_path = os.path.join(build_dir, '_build_script.sh')
        with open(build_script_path, 'w') as f:
            f.write(build_script.format(build_dir=build_dir, package_name=package_name))
        subprocess.run('cd {} && bash _build_script.sh'.format(build_dir), shell=True)
