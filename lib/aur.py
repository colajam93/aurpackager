import json
import os.path
import subprocess
import tempfile
from contextlib import closing
from urllib.parse import quote
from urllib.request import HTTPBasicAuthHandler, build_opener, HTTPPasswordMgrWithDefaultRealm, OpenerDirector

from typing import List, Dict

from lib.download import save_to_file
from manager.models import Package
from packager.settings_local import UNOFFICIAL_AUR_SERVERS
from packager.settings_util import AURServer

_AUR_SERVERS: Dict[str, AURServer] = {Package.OFFICIAL: AURServer('https://aur.archlinux.org')}
_AUR_SERVERS.update(UNOFFICIAL_AUR_SERVERS)


def _aur_server(aur_server_tag: str) -> AURServer:
    # TODO: error report for unrecognized AUR server tag
    return _AUR_SERVERS.get(aur_server_tag, _AUR_SERVERS[Package.OFFICIAL])


def _aur_url(aur_server_tag: str) -> str:
    return _aur_server(aur_server_tag).address


def _base_url(aur_server_tag: str) -> str:
    return _aur_url(aur_server_tag) + '/rpc/?v=5&'


# TODO: add type hint
def _query_info(packages: List[str], aur_server_tag: str):
    url = _base_url(aur_server_tag) + 'type=info&' + '&'.join(['arg[]={}'.format(quote(x)) for x in packages])
    return _send_query(url, aur_server_tag)


# TODO: add type hint
def _query_search(package: str, aur_server_tag: str):
    url = _base_url(aur_server_tag) + 'type=search&' + 'arg={}'.format(quote(package))
    return _send_query(url, aur_server_tag)


# TODO: add type hint
def _send_query(url: str, aur_server_tag: str):
    opener = _create_opener(aur_server_tag)
    with closing(opener.open(fullurl=url)) as request:
        return json.loads(request.read().decode())


def _create_opener(aur_server_tag: str) -> OpenerDirector:
    server = _aur_server(aur_server_tag)
    password_manager = HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(realm=None,
                                  uri=server.address,
                                  user=server.user,
                                  passwd=server.password)
    handler = HTTPBasicAuthHandler(password_manager)
    return build_opener(handler)


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


def info(package: str, aur_server_tag: str) -> AURInfo:
    result = _query_info([package], aur_server_tag)
    if result['resultcount'] == 0:
        raise PackageNotFoundError
    return AURInfo(result['results'][0], aur_server_tag)


def detail_info(package: str, aur_server_tag: str) -> DetailAURInfo:
    info_ = info(package, aur_server_tag)
    with tempfile.TemporaryDirectory() as temp_dir:
        tar_path = os.path.join(temp_dir, 'tarball')
        opener = _create_opener(aur_server_tag)
        save_to_file(info_.tar_url, tar_path, opener=opener)
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
    result = _query_info(packages, aur_server_tag)

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
    result = _query_search(package, aur_server_tag)
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
