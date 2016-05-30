from manager.models import Package
from urllib.request import urlopen
from contextlib import closing
import json
import os
import subprocess
import packager.path

AUR_URL = 'https://aur.archlinux.org'
RPC_URL = AUR_URL + '/rpc/?v=5&type=info&arg[]={}'


class BuilderError(Exception):
    pass


class Builder:
    def __init__(self, package_id):
        self.package = Package.objects.get(id=package_id)
        self.log_path = ''
        self.version = ''
        self.result_path = ''

    @property
    def package_name(self):
        return self.package.name

    def build(self, date):
        # get package info from AUR
        with closing(urlopen(RPC_URL.format(self.package_name))) as request:
            result = json.loads(request.read().decode())

        # package detail dictionary
        if not len(result['results']) == 1:
            raise BuilderError
        detail = result['results'][0]

        # get tarball url and package version
        tar_url = AUR_URL + detail['URLPath']
        self.version = detail['Version']

        path = packager.path.Path(self.package_name, self.version, date.isoformat())
        build_dir = path.build_dir
        tar_path = path.tar_file
        dest_dir = path.dest_dir
        self.log_path = path.log_file

        # create working directories
        os.makedirs(build_dir, 0o700)
        os.makedirs(dest_dir, 0o700)

        # get tarball
        with closing(urlopen(tar_url)) as request:
            with open(tar_path, 'wb') as f:
                f.write(request.read())

        # build script
        build_script = '''
#!/bin/bash

cd {build_dir}
tar xvf {package_name}
cd {package_name}
export PKGDEST='{dest}'
makepkg -s --noconfirm
'''
        build_script_path = path.script_file
        with open(build_script_path, 'w') as f:
            f.write(build_script.format(build_dir=build_dir, package_name=self.package_name, dest=dest_dir))

        # execute build script
        completed = subprocess.run('cd {} && bash _build_script.sh'.format(build_dir), shell=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

        # write log
        with open(self.log_path, 'w') as f:
            f.write(json.dumps(result, indent=4))
            f.write('\n')
            f.write(completed.stdout)

        self.result_path = path.result_file
