from django.shortcuts import render, redirect
from manager.models import Package, Build
from django.http import HttpResponse
import os.path
from django.core.files import File
import packager.path


def package_list(request):
    packages = Package.objects.all().order_by('id')
    for package in packages:
        builds = Build.objects.filter(package_id=package.id).order_by('-id')
        if len(builds) >= 1:
            setattr(package, 'status', builds[0].status)
        else:
            setattr(package, 'status', 'None')

    return render(request, 'package_list.html', {'packages': packages, 'active': 'list'})


def package_detail(request, package_name):
    package = Package.objects.get(name=package_name)
    builds = Build.objects.filter(package_id=package.id).order_by('-id')
    for build, number in zip(builds, range(1, len(builds) + 1)):
        build.number = number
    return render(request, 'package_detail.html', {'package': package, 'builds': builds, 'active': 'list'})


def package_register(request):
    return render(request, 'package_register.html', {'active': 'register'})


def package_register_detail(request, package_name):
    return render(request, 'package_register_detail.html', {'package_name': package_name, 'active': 'register'})


def build_detail(request, package_name, build_number):
    package = Package.objects.get(name=package_name)
    try:
        build = Build.objects.filter(package_id=package.id).order_by('-id')[int(build_number) - 1]
        build.number = build_number
    except IndexError:
        return redirect('manager:package_list')
    path = packager.path.build_to_path(build)
    log = ''
    if not build.status == Build.BUILDING:
        try:
            with open(path.log_file, 'r') as f:
                log = f.read()
        except FileNotFoundError:
            pass
    is_success = build.status == Build.SUCCESS
    return render(request, 'build_detail.html',
                  {'build': build, 'package': build.package, 'log': log, 'is_success': is_success,
                   'active': 'list'})


def build_download(request, package_name, build_number):
    package = Package.objects.get(name=package_name)
    try:
        build = Build.objects.filter(package_id=package.id).order_by('-id')[int(build_number) - 1]
    except IndexError:
        build = None
    if build and build.status == Build.SUCCESS:
        path = packager.path.build_to_path(build)
        result_file = path.result_file
        with open(result_file, 'rb') as f:
            ff = File(f)
            response = HttpResponse(ff, content_type='application/x-xz')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(os.path.basename(result_file))
            response['Content-Length'] = ff.size
            return response
    else:
        return HttpResponse(status=404)
