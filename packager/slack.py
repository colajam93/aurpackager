import json
import urllib.error
import urllib.parse
import urllib.request

from django.core.urlresolvers import reverse_lazy

from lib.aur import aur_package_url
from manager.models import Build, Artifact
from packager.settings import SLACK_NOTIFICATION_URL, AUR_PACKAGER_BASE_URL, SLACK_NOTIFICATION


def post(build: Build):
    if not SLACK_NOTIFICATION and SLACK_NOTIFICATION_URL and AUR_PACKAGER_BASE_URL:
        return
    detail_url = AUR_PACKAGER_BASE_URL + str(reverse_lazy('manager:build_detail',
                                                          kwargs={'package_name': build.package.name,
                                                                  'build_number': 1}))
    base = '<{}|{}> {}: <{}|{}>'.format(aur_package_url(build.package.name), build.package.name,
                                        build.version, detail_url, build.status)

    if build.status == Build.SUCCESS:
        emoji = ':+1:'
        sha256s = json.loads(build.sha256)
        artifacts = []
        for artifact in Artifact.objects.filter(package=build.package):
            download_url = AUR_PACKAGER_BASE_URL + str(reverse_lazy('manager:build_download',
                                                                    kwargs={'package_name': artifact.name,
                                                                            'build_number': 1}))
            sha256 = sha256s[artifact.name]
            s = '<{}|:arrow_down: {}> sha256: {}'.format(download_url, artifact.name, sha256)
            artifacts.append(s)
        text = '\n'.join([base] + artifacts)
    else:
        emoji = ':ghost:'
        text = base
    name = '{}: {} {}'.format(build.status, build.package.name, build.version)

    data = {'text': text, 'username': name, 'icon_emoji': emoji}
    request = urllib.request.Request(SLACK_NOTIFICATION_URL)
    request.add_header('Content-type', 'application/json')
    try:
        urllib.request.urlopen(request, json.dumps(data).encode())
    except urllib.error.URLError:
        pass
