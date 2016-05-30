import os.path
from packager.settings import BUILD_ROOT_DIR


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
        self.dest_dir = os.path.join(self.build_dir, '_dest')

    @property
    def tar_file(self):
        return os.path.join(self.build_dir, self.name)

    @property
    def result_file(self):
        dest_list = os.listdir(self.dest_dir)
        try:
            dest_filename = next(x for x in dest_list if x.endswith('pkg.tar.xz'))
        except StopIteration:  # not found
            raise FileNotFoundError
        return os.path.join(self.dest_dir, dest_filename)

    @property
    def log_file(self):
        return os.path.join(self.dest_dir, 'build.log')

    @property
    def script_file(self):
        return os.path.join(self.build_dir, '_build_script.sh')


def build_to_path(build, base=BUILD_ROOT_DIR):
    return Path(build.package.name, build.version, build.date.isoformat(), base=base)
