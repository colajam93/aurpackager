from django.http import HttpResponse
from django.template import RequestContext, Template
import json
import lib.aur.query as query
import manager.operation as operation


def package_search(request):
    if request.method == 'POST':
        method = request.POST
    else:
        method = request.GET

    if 'name' not in method or not method['name']:
        return HttpResponse(status=400)
    else:
        result = query.search(method['name'])
        c = RequestContext(request, {'result': json.dumps(result)})
        t = Template('{{result | safe}}')
        return HttpResponse(t.render(c), content_type='application/json')


def package_info(request):
    if request.method == 'POST':
        method = request.POST
    else:
        method = request.GET

    if 'name' not in method or not method['name']:
        return HttpResponse(status=400)
    else:
        result = query.info(method['name'])
        c = RequestContext(request, {'result': json.dumps(result)})
        t = Template('{{result | safe}}')
        return HttpResponse(t.render(c), content_type='application/json')


def package_register(request):
    if request.method == 'POST':
        method = request.POST
    else:
        method = request.GET

    if 'name' not in method or not method['name']:
        return HttpResponse(status=400)
    else:
        with_depend = 'depend' in method and method['depend'] == 'true'
        ret = dict()
        try:
            r = operation.register(method['name'], with_depend=with_depend)
        except operation.OperationError as e:
            ret['result'] = False
            ret['detail'] = str(e)
        else:
            ret.update(r)
            ret['name'] = method['name']
            ret['result'] = True

        c = RequestContext(request, {'result': json.dumps(ret)})
        t = Template('{{result | safe}}')
        response = HttpResponse(t.render(c), content_type='application/json')
        if not ret['result']:
            response.status_code = 400
        return response


def package_remove(request):
    if request.method == 'POST':
        method = request.POST
    else:
        method = request.GET

    if 'name' not in method or not method['name']:
        return HttpResponse(status=400)
    else:
        cleanup = 'cleanup' in method and method['cleanup'] == 'true'
        ret = dict()
        try:
            operation.remove(method['name'], cleanup=cleanup)
        except operation.OperationError as e:
            ret['result'] = False
            ret['detail'] = str(e)
        else:
            ret['name'] = method['name']
            ret['result'] = True

        c = RequestContext(request, {'result': json.dumps(ret)})
        t = Template('{{result | safe}}')
        response = HttpResponse(t.render(c), content_type='application/json')
        if not ret['result']:
            response.status_code = 400
        return response


def package_build(request):
    if request.method == 'POST':
        method = request.POST
    else:
        method = request.GET

    if 'name' not in method or not method['name']:
        return HttpResponse(status=400)
    else:
        ret = dict()
        try:
            operation.build(method['name'])
        except operation.OperationError as e:
            ret['result'] = False
            ret['detail'] = str(e)
        else:
            ret['name'] = method['name']
            ret['result'] = True

        c = RequestContext(request, {'result': json.dumps(ret)})
        t = Template('{{result | safe}}')
        response = HttpResponse(t.render(c), content_type='application/json')
        if not ret['result']:
            response.status_code = 400
        return response
