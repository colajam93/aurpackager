import json
import os.path
from typing import Union

from django.forms.models import model_to_dict
from django.http import HttpResponse, FileResponse, HttpRequest
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie

import packager.path
from manager.models import Package, Build, Artifact
from packager.settings_local import CUSTOM_LOCAL_REPOSITORY_DIR, CUSTOM_LOCAL_REPOSITORY


@ensure_csrf_cookie
def package_list(request):
    packages = Package.objects.all().order_by('id')
    for package in packages:
        builds = Build.objects.filter(package_id=package.id).order_by('-id')
        if len(builds) >= 1:
            setattr(package, 'status', builds[0].status)
        else:
            setattr(package, 'status', 'None')

    return render(request, 'package_list.html', {'packages': packages, 'active': 'list'})


@ensure_csrf_cookie
def package_detail(request, package_name):
    package = Package.objects.get(name=package_name)
    builds = Build.objects.filter(package_id=package.id).order_by('-id')
    if Build.objects.filter(package_id=package.id, status=Build.SUCCESS).exists():
        artifacts = Artifact.objects.filter(package=package)
    else:
        artifacts = []
    for build, number in zip(builds, range(1, len(builds) + 1)):
        build.number = number
    return render(request, 'package_detail.html',
                  {'package': package, 'builds': builds, 'active': 'list', 'artifacts': artifacts})


@ensure_csrf_cookie
def package_register(request):
    return render(request, 'package_register.html', {'active': 'register'})


@ensure_csrf_cookie
def package_register_detail(request, package_name):
    return render(request, 'package_register_detail.html', {'package_name': package_name, 'active': 'register'})


@ensure_csrf_cookie
def build_detail(request, package_name, build_number):
    package = Package.objects.get(name=package_name)
    try:
        build = Build.objects.filter(package_id=package.id).order_by('-id')[int(build_number) - 1]
        build.number = build_number
    except IndexError:
        return redirect('manager:package_list')
    is_success = build.status == Build.SUCCESS
    artifacts = []
    try:
        sha256s = json.loads(build.sha256)
    except json.JSONDecodeError:
        sha256s = {}
    for artifact in Artifact.objects.filter(package=package):
        a = model_to_dict(artifact)
        a['sha256'] = sha256s.get(a['name'], '')
        artifacts.append(a)

    return render(request, 'build_detail.html',
                  {'build': build, 'package': build.package, 'is_success': is_success, 'active': 'list',
                   'artifacts': artifacts})


@ensure_csrf_cookie
def build_log(request, package_name, build_number):
    try:
        build = Build.objects.filter(package__name=package_name).order_by('-id')[int(build_number) - 1]
        build.number = build_number
    except IndexError:
        build = None
    if build and not build.status == Build.BUILDING:
        path = packager.path.build_to_path(build)
        try:
            with open(path.log_file, 'r') as f:
                log = f.read()
        except FileNotFoundError:
            log = ''
        return render(request, 'build_log.html',
                      {'build': build, 'package': build.package, 'log': log, 'active': 'list'})
    else:
        return HttpResponse(status=404)


def _package_response(path: str) -> Union[HttpResponse, FileResponse]:
    """
    :param path: full path to package file
    :return: FileResponse or HttpResponse(error)
    """
    try:
        f = open(path, 'rb')
        response = FileResponse(f, content_type='application/x-xz')
        response['Content-Length'] = os.path.getsize(path)
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(path))
        return response
    except FileNotFoundError:
        return HttpResponse(status=404)
    except PermissionError:
        return HttpResponse(status=403)


@ensure_csrf_cookie
def build_download(request: HttpRequest, package_name: str, build_number: str) -> Union[HttpResponse, FileResponse]:
    artifact = Artifact.objects.get(name=package_name)
    try:
        build = Build.objects.filter(package_id=artifact.package.id).order_by('-id')[int(build_number) - 1]
    except IndexError:
        build = None
    if build and build.status == Build.SUCCESS:
        path = packager.path.build_to_path(build)
        result_file = path.artifact_file(artifact.name)
        return _package_response(result_file)
    else:
        return HttpResponse(status=404)


@ensure_csrf_cookie
def repository(request: HttpRequest, file_name: str) -> Union[HttpResponse, FileResponse]:
    if not CUSTOM_LOCAL_REPOSITORY:
        return HttpResponse(status=404)
    path = os.path.join(CUSTOM_LOCAL_REPOSITORY_DIR, file_name)
    return _package_response(path)
