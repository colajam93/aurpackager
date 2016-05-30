import os.path


class Path:
    def __init__(self, base, name, version, date):
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


def get_path(base, build):
    return Path(base, build.package.name, build.version, build.date.isoformat())
