from django.http import HttpResponse
from django.template import RequestContext, Template
import json
import lib.aur as aur
import manager.operation as operation
import functools


def make_api(require=None, optional=None, error_check=False, status=400):
    if optional is None:
        optional = []
    if require is None:
        require = []

    def decorator(function):
        @functools.wraps(function)
        def wrapper(request):
            if request.method == 'POST':
                params = request.POST
            else:
                params = request.GET
            for key in require:
                if key not in params or not params[key]:
                    return HttpResponse(status=status)
            option_dict = dict()
            for key in optional:
                if key in params:
                    option_dict[key] = params[key]
            result = function(params, **option_dict)
            c = RequestContext(request, {'result': json.dumps(result)})
            t = Template('{{result | safe}}')
            response = HttpResponse(t.render(c), content_type='application/json')
            if error_check:
                if not result['result']:
                    response.status_code = status
            return response

        return wrapper

    return decorator


@make_api(require=['name'])
def package_search(params):
    return aur.search(params['name'])


@make_api(require=['name'])
def package_info(params):
    return aur.info(params['name'])


@make_api(require=['name'], optional=['depend'], error_check=True)
def package_register(params, **kwargs):
    with_depend = kwargs['depend'] == 'true'
    ret = dict()
    try:
        r = operation.register(params['name'], with_depend=with_depend)
    except operation.OperationError as e:
        ret['result'] = False
        ret['detail'] = str(e)
    else:
        ret.update(r)
        ret['result'] = True
        ret['name'] = params['name']
    return ret


@make_api(require=['name'], optional=['cleanup'], error_check=True)
def package_remove(params, **kwargs):
    cleanup = kwargs['cleanup'] == 'true'
    ret = dict()
    try:
        operation.remove(params['name'], cleanup=cleanup)
    except operation.OperationError as e:
        ret['result'] = False
        ret['detail'] = str(e)
    else:
        ret['result'] = True
        ret['name'] = params['name']
    return ret


@make_api(require=['name'], error_check=True)
def package_build(params):
    ret = dict()
    try:
        operation.build(params['name'])
    except operation.OperationError as e:
        ret['result'] = False
        ret['detail'] = str(e)
    else:
        ret['result'] = True
        ret['name'] = params['name']
    return ret


@make_api()
def package_build_all(_):
    operation.build_all()
