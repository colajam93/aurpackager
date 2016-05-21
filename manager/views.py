from django.shortcuts import render, redirect
from manager.models import Package, Build
from packager.manager import BuilderManager


def package_list(request):
    packages = Package.objects.all().order_by('id')
    return render(request, 'package_list.html', {'packages': packages})


def package_detail(request, package_name):
    package = Package.objects.get(name=package_name)
    builds = Build.objects.filter(package_id=package.id).order_by('-date')
    for build, number in zip(builds, range(1, len(builds) + 1)):
        build.number = number
    return render(request, 'package_detail.html', {'package_name': package_name, 'builds': builds})


def package_build(request, package_name):
    package = Package.objects.get(name=package_name)
    if package:
        BuilderManager().register(package.id)
        return render(request, 'package_build.html', {'package': package})
    else:
        return redirect('manager:package_list')


def build_detail(request, package_name, build_number):
    package = Package.objects.get(name=package_name)
    try:
        build = Build.objects.filter(package_id=package.id).order_by('-date')[int(build_number) - 1]
    except IndexError:
        build = None
    if build:
        return render(request, 'build_detail.html', {'build': build, 'package': build.package})
    else:
        return redirect('manager:package_list')
