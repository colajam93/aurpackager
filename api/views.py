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
        ret = dict()
        try:
            operation.register(method['name'])
        except operation.OperationError as e:
            ret['result'] = False
            ret['error'] = e
        else:
            ret['result'] = True

        c = RequestContext(request, {'result': json.dumps({'result': ret})})
        t = Template('{{result | safe}}')
        return HttpResponse(t.render(c), content_type='application/json')
