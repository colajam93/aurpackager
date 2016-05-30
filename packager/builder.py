from manager.models import Package
from urllib.request import urlopen
from contextlib import closing
import json
import os
import subprocess
import packager.path
import lib.aur.query as aur


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
        info = aur.info(self.package_name)

        # get tarball url and package version
        self.version = info.Version

        path = packager.path.Path(self.package_name, self.version, date.isoformat())
        build_dir = path.build_dir
        tar_path = path.tar_file
        dest_dir = path.dest_dir
        self.log_path = path.log_file

        # create working directories
        os.makedirs(build_dir, 0o700)
        os.makedirs(dest_dir, 0o700)

        # get tarball
        with closing(urlopen(info.tar_url)) as request:
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
            f.write(json.dumps(info, indent=4))
            f.write('\n')
            f.write(completed.stdout)

        self.result_path = path.result_file
