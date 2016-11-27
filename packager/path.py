import os.path

from manager.models import Artifact
from packager.settings import BUILD_ROOT_DIR

DEST_DIR_NAME = '_dest'


# path structure:
# build_dir = [BUILD_ROOT_DIR]/[package_name]/[version]/[date]
# script_file = [build_dir]/_build_script.sh
# dest = [build_dir]/[package].pkg.tar.xz,build.log
# work_dir = [build_dir]/[package_name]/PKGBUILD,etc.
class Path:
    def __init__(self, name, version, date, base=BUILD_ROOT_DIR):
        build_dir = os.path.join(base, name, version, date)
        self.name = name
        self.build_dir = build_dir.translate(str.maketrans(':', '_'))
        self.dest_dir = os.path.join(self.build_dir, DEST_DIR_NAME)

    @property
    def tar_file(self):
        return os.path.join(self.build_dir, self.name)

    def artifact_file(self, name):
        fns = [fn for fn in os.listdir(self.dest_dir) if
               fn.startswith('{}-'.format(name)) and fn.endswith('.pkg.tar.xz')]
        if len(fns) == 1:  # success to find unique pkg
            return os.path.join(self.dest_dir, fns[0])
        else:  # there are multiple candidates for path
            artifact_names = map(lambda x: x.name, Artifact.objects.filter(package__name=self.name).exclude(
                name=name))  # get artifact names exclude required one
            for an in artifact_names:  # exclude not required names from candidates
                fns = [f for f in fns if not f.startswith(an)]
            if len(fns) == 1:
                return os.path.join(self.dest_dir, fns[0])
            else:
                raise FileNotFoundError

    @property
    def log_file(self):
        return os.path.join(self.dest_dir, 'build.log')

    @property
    def script_file(self):
        return os.path.join(self.build_dir, '_build_script.sh')


def build_to_path(build, base=BUILD_ROOT_DIR):
    return Path(build.package.name, build.version, build.date.isoformat(), base=base)
