from urllib.request import urlopen
from contextlib import closing
import json

AUR_URL = 'https://aur.archlinux.org'
BASE_URL = AUR_URL + '/rpc/?v=5&'
INFO_URL = BASE_URL + 'type=info&'
SEARCH_URL = BASE_URL + 'type=search&'


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


def __aur_query(url):
    with closing(urlopen(url)) as request:
        result = json.loads(request.read().decode())
    return result


def info(package):
    url = INFO_URL + 'arg[]={}'.format(package)
    result = __aur_query(url)
    if result['resultcount'] == 0:
        raise PackageNotFoundError
    return AURInfo(result['results'][0])


def multiple_info(packages):
    url = INFO_URL + '&'.join(map(lambda x: 'arg[]={}'.format(x), packages))
    result = __aur_query(url)

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
    result = __aur_query(url)
    return [AURInfo(x) for x in result['results']]
