import urllib.parse
import urllib.request
import json
from django.core.urlresolvers import reverse_lazy
from manager.models import Build

from packager.settings import SLACK_NOTIFICATION_URL, AUR_PACKAGER_BASE_URL


def post(build):
    assert SLACK_NOTIFICATION_URL
    assert AUR_PACKAGER_BASE_URL
    detail_url = AUR_PACKAGER_BASE_URL + str(reverse_lazy('manager:build_detail',
                                                          kwargs={'package_name': build.package.name,
                                                                  'build_number': 1}))
    download_url = AUR_PACKAGER_BASE_URL + str(reverse_lazy('manager:build_download',
                                                            kwargs={'package_name': build.package.name,
                                                                    'build_number': 1}))
    text = '{}: {} <{}|Detail> <{}|Download>\n{}'.format(build.status, build.package.name, detail_url, download_url,
                                                         build.sha256)
    if build.status == Build.SUCCESS:
        emoji = ':+1:'
    else:
        emoji = ':ghost:'
    name = '{}: {} {}'.format(build.status, build.package.name, build.version)

    data = {'text': text, 'username': name, 'icon_emoji': emoji}
    request = urllib.request.Request(SLACK_NOTIFICATION_URL)
    request.add_header('Content-type', 'application/json')
    urllib.request.urlopen(request, json.dumps(data).encode())
