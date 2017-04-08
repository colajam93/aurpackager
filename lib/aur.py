import json
import os.path
import subprocess
import tempfile
from contextlib import closing
from urllib.parse import quote
from urllib.request import urlopen

from typing import List, Dict

from lib.download import save_to_file
from manager.models import Package
from packager.settings_local import UNOFFICIAL_AUR_SERVERS
from packager.settings_util import AURServer

_AUR_SERVERS: Dict[str, AURServer] = {Package.OFFICIAL: AURServer('https://aur.archlinux.org')}
_AUR_SERVERS.update(UNOFFICIAL_AUR_SERVERS)


def _aur_url(aur_server_tag: str) -> str:
    # TODO: error report for unrecognized AUR server tag
    server = _AUR_SERVERS.get(aur_server_tag, _AUR_SERVERS[Package.OFFICIAL])
    return server.address


def _base_url(aur_server_tag: str) -> str:
    return _aur_url(aur_server_tag) + '/rpc/?v=5&'


def _info_url(aur_server_tag: str) -> str:
    return _base_url(aur_server_tag) + 'type=info&'


def _search_url(aur_server_tag: str) -> str:
    return _base_url(aur_server_tag) + 'type=search&'


def package_url(aur_server_tag: str, package_name: str) -> str:
    return _aur_url(aur_server_tag) + '/packages/{}'.format(package_name)


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
    def __init__(self, package_dict: Dict[str, str], aur_server_tag: str) -> None:
        super().__init__(package_dict)
        self.tar_url = _aur_url(aur_server_tag) + self.URLPath
        self.aur_url = package_url(aur_server_tag, self.Name)


class DetailAURInfo(AURInfo):
    def __init__(self, package_dict: Dict[str, str], pkgnames: List[str], aur_server_tag: str) -> None:
        super().__init__(package_dict, aur_server_tag)
        self.pkgnames = pkgnames


# TODO: add type hint(maybe complex)
def _aur_query(url: str):
    with closing(urlopen(quote(url, safe='/?:&=[]'))) as request:
        return json.loads(request.read().decode())


def info(package: str, aur_server_tag: str) -> AURInfo:
    url = _info_url(aur_server_tag) + 'arg[]={}'.format(package)
    result = _aur_query(url)
    if result['resultcount'] == 0:
        raise PackageNotFoundError
    return AURInfo(result['results'][0], aur_server_tag)


def detail_info(package: str, aur_server_tag: str) -> DetailAURInfo:
    info_ = info(package, aur_server_tag)
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
    return DetailAURInfo(info_, pkgnames, aur_server_tag)


def multiple_info(packages: List[str], aur_server_tag: str) -> Dict[str, AURInfo]:
    url = _info_url(aur_server_tag) + '&'.join(map(lambda x: 'arg[]={}'.format(x), packages))
    result = _aur_query(url)

    # dict which key is the package name
    ret = dict()
    for package in (AURInfo(x, aur_server_tag) for x in result['results']):
        ret[package.Name] = package
        packages.remove(package.Name)
    # if package is not found, insert None instead
    for package in packages:
        if package not in ret:
            ret[package] = None
    return ret


def search(package: str, aur_server_tag: str) -> List[AURInfo]:
    url = _search_url(aur_server_tag) + 'arg={}'.format(package)
    result = _aur_query(url)
    return [AURInfo(x, aur_server_tag) for x in result['results']]


def exist(package: str, aur_server_tag: str) -> bool:
    try:
        info(package, aur_server_tag)
    except PackageNotFoundError:
        return False
    else:
        return True


def servers() -> List[str]:
    return list(_AUR_SERVERS.keys())
