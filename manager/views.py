from django.shortcuts import render, redirect
from manager.models import Package, Build
from packager.manager import BuilderManager
from django.http import HttpResponse
import json
import os.path
from django.core.files import File


def package_list(request):
    packages = Package.objects.all().order_by('id')
    for package in packages:
        builds = Build.objects.filter(package_id=package.id).order_by('-date')
        if len(builds) >= 1:
            setattr(package, 'status', builds[0].status)
        else:
            setattr(package, 'status', 'None')

    return render(request, 'package_list.html', {'packages': packages})


def package_detail(request, package_name):
    package = Package.objects.get(name=package_name)
    builds = Build.objects.filter(package_id=package.id).order_by('-date')
    for build, number in zip(builds, range(1, len(builds) + 1)):
        build.number = number
    return render(request, 'package_detail.html', {'package': package, 'builds': builds})


def package_build(request, package_name):
    package = Package.objects.get(name=package_name)
    if package:
        BuilderManager().register(package.id)
        return HttpResponse(json.dumps({'result': True}), content_type='application/javascript')
    else:
        return HttpResponse(json.dumps({'result': False}), content_type='application/javascript')


def package_register(request):
    return render(request, 'package_register.html')


def package_register_detail(request, package_name):
    return render(request, 'package_register_detail.html', {'package_name': package_name})


def build_detail(request, package_name, build_number):
    package = Package.objects.get(name=package_name)
    try:
        build = Build.objects.filter(package_id=package.id).order_by('-date')[int(build_number) - 1]
        build.number = build_number
    except IndexError:
        build = None
    log = ''
    if not build.status == Build.BUILDING:
        try:
            with open(build.log_path, 'r') as f:
                log = f.read()
        except FileNotFoundError:
            pass
    if build:
        is_success = build.status == Build.SUCCESS
        return render(request, 'build_detail.html',
                      {'build': build, 'package': build.package, 'log': log, 'is_success': is_success})
    else:
        return redirect('manager:package_list')


def build_download(request, package_name, build_number):
    package = Package.objects.get(name=package_name)
    try:
        build = Build.objects.filter(package_id=package.id).order_by('-date')[int(build_number) - 1]
    except IndexError:
        build = None
    if build and build.status == Build.SUCCESS:
        with open(build.result_path, 'rb') as f:
            ff = File(f)
            response = HttpResponse(ff, content_type='application/x-xz')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(build.result_path))
            response['Content-Length'] = ff.size
            return response
    else:
        return HttpResponse(status=404)


def build_install(request, package_name, build_number):
    package = Package.objects.get(name=package_name)
    try:
        build = Build.objects.filter(package_id=package.id).order_by('-date')[int(build_number) - 1]
    except IndexError:
        build = None
    if build and build.status == Build.SUCCESS:
        import subprocess
        subprocess.Popen('sudo -S pacman -U --noconfirm {}'.format(build.result_path), shell=True, close_fds=True,
                         stdin=None, stdout=None, stderr=None)
        return HttpResponse(json.dumps({'result': True}), content_type='application/javascript')
    else:
        return HttpResponse(status=404)


def build_all(request):
    packages = Package.objects.all()
    for package in packages:
        BuilderManager().register(package.id)
    return HttpResponse(json.dumps({'result': True}), content_type='application/javascript')
