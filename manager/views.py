from django.shortcuts import render
from django.http import HttpResponse

from manager.models import Package


def package_list(request):
    packages = Package.objects.all().order_by('id')
    return render(request, 'package_list.html', {'packages': packages})
    return HttpResponse('Package list')


def package_detail(request, package_id):
    return HttpResponse('Package detail')


def build_detail(request, package_id, build_id):
    return HttpResponse('Build detail')
