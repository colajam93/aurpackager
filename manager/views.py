from django.shortcuts import render, redirect
from manager.models import Package, Build


def package_list(request):
    packages = Package.objects.all().order_by('id')
    return render(request, 'package_list.html', {'packages': packages})


def package_detail(request, package_id):
    builds = Build.objects.filter(package_id=package_id).order_by('id')
    if builds:
        return render(request, 'package_detail.html', {'package_id': package_id, 'builds': builds})
    else:
        return redirect('manager:package_list')


def build_detail(request, package_id, build_id):
    build = Build.objects.get(id=build_id)
    if build:
        return render(request, 'build_detail.html', {'build': build, 'package': build.package})
    else:
        return redirect('manager:package_list')
