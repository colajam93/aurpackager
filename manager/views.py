from django.shortcuts import render, redirect
from django.http import HttpResponse

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
    return HttpResponse('Build detail')
