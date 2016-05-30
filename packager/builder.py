from manager.models import Package
import json
import os
import subprocess
import packager.path
import lib.aur as aur
import lib.download as download


class BuilderError(Exception):
    pass


class Builder:
    def __init__(self, package_id):
        self.package = Package.objects.get(id=package_id)
        self.version = ''

    @property
    def package_name(self):
        return self.package.name

    def build(self, date):
        # get package info from AUR
        info = aur.info(self.package_name)

        # create required path
        self.version = info.Version
        path = packager.path.Path(self.package_name, self.version, date.isoformat())
        build_dir = path.build_dir
        dest_dir = path.dest_dir

        # create working directories
        os.makedirs(build_dir, 0o700)
        os.makedirs(dest_dir, 0o700)

        # get tarball
        download.save_to_file(info.tar_url, path.tar_file)

        # generate build script
        build_script = '''
#!/bin/bash

cd {build_dir}
tar xvf {package_name}
cd {package_name}
export PKGDEST='{dest}'
makepkg -s --noconfirm
'''
        with open(path.script_file, 'w') as f:
            f.write(build_script.format(build_dir=build_dir, package_name=self.package_name, dest=dest_dir))

        # execute build script
        completed = subprocess.run('cd {} && bash _build_script.sh'.format(build_dir), shell=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

        # write log
        with open(path.log_file, 'w') as f:
            f.write(json.dumps(info, indent=4))
            f.write('\n')
            f.write(completed.stdout)
