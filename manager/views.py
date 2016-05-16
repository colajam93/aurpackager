from django.shortcuts import render
from django.http import HttpResponse


def package_list(request):
    return HttpResponse('Package list')


def package_detail(request, package_id):
    return HttpResponse('Package detail')


def build_detail(request, build_id):
    return HttpResponse('Build detail')
