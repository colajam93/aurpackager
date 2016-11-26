import json
import os.path
import subprocess
import tempfile
from contextlib import closing
from urllib.request import urlopen

from lib.download import save_to_file

AUR_URL = 'https://aur.archlinux.org'
BASE_URL = AUR_URL + '/rpc/?v=5&'
INFO_URL = BASE_URL + 'type=info&'
SEARCH_URL = BASE_URL + 'type=search&'


def aur_package_url(name):
    return AUR_URL + '/packages/{}'.format(name)


class PackageNotFoundError(Exception):
    pass


class AttrDict(dict):
    """
    http://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute-in-python
    """

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class AURInfo(AttrDict):
    def __init__(self, package_dict):
        super().__init__(package_dict)
        self.tar_url = AUR_URL + self.URLPath
        self.aur_url = aur_package_url(self.Name)


class DetailAURInfo(AURInfo):
    def __init__(self, package_dict, pkgnames):
        super().__init__(package_dict)
        self.pkgnames = pkgnames


def _aur_query(url):
    with closing(urlopen(url)) as request:
        result = json.loads(request.read().decode())
    return result


def info(package: str) -> AURInfo:
    url = INFO_URL + 'arg[]={}'.format(package)
    result = _aur_query(url)
    if result['resultcount'] == 0:
        raise PackageNotFoundError
    return AURInfo(result['results'][0])


def detail_info(package: str) -> DetailAURInfo:
    info_ = info(package)
    with tempfile.TemporaryDirectory() as temp_dir:
        tar_path = os.path.join(temp_dir, 'tarball')
        save_to_file(info_.tar_url, tar_path)
        tar_out = os.path.join(temp_dir, 'o')
        os.mkdir(tar_out)
        subprocess.run(['tar', 'xvf', tar_path, '-C', tar_out], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pkgbuild = ''
        # Only one directory exists in tar_out directory and it contains the PKGBUILD.
        for d in (os.path.join(tar_out, f) for f in os.listdir(tar_out)):
            if os.path.isdir(d):
                pkgbuild = os.path.join(d, 'PKGBUILD')
        s = '''
            source {pkgbuild}
            if [[ "$(declare -p pkgname)" =~ "declare -a" ]]; then
                printf '%s\n' "${{pkgname[@]}}"
            else
                echo $pkgname
            fi
            '''.format(pkgbuild=pkgbuild)
        with tempfile.NamedTemporaryFile(mode='w') as temp_file:
            temp_file.write(s)
            temp_file.flush()
            completed = subprocess.run(['bash', temp_file.name], universal_newlines=True, stdout=subprocess.PIPE)
            pkgnames = completed.stdout.strip().split('\n')
    return DetailAURInfo(info_, pkgnames)


def multiple_info(packages):
    url = INFO_URL + '&'.join(map(lambda x: 'arg[]={}'.format(x), packages))
    result = _aur_query(url)

    # dict which key is the package name
    ret = dict()
    for package in (AURInfo(x) for x in result['results']):
        ret[package.Name] = package
        packages.remove(package.Name)
    # if package is not found, insert None instead
    for package in packages:
        if package not in ret:
            ret[package] = None
    return ret


def search(package):
    url = SEARCH_URL + 'arg={}'.format(package)
    result = _aur_query(url)
    return [AURInfo(x) for x in result['results']]


def exist(package):
    try:
        info(package)
    except PackageNotFoundError:
        return False
    else:
        return True
