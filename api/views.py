import functools

from django.http import HttpResponse, JsonResponse

import lib.aur as aur
import manager.operation as operation


def make_api(require=None, optional=None, error_check=False, status=400):
    if optional is None:
        optional = []
    if require is None:
        require = []

    def decorator(f):
        @functools.wraps(f)
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
            result = f(params, **option_dict)
            response = JsonResponse(result, safe=False)
            if error_check:
                if not result['result']:
                    response.status_code = status
            return response

        return wrapper

    return decorator


@make_api(require=['name', 'server'])
def package_search(params):
    return aur.search(params['name'], params['server'])


@make_api(require=['name', 'server'])
def package_info(params):
    return aur.info(params['name'], params['server'])


@make_api(require=['name', 'server'], optional=['depend'], error_check=True)
def package_register(params, **kwargs):
    with_depend = kwargs['depend'] == 'true'
    ret = dict()
    try:
        r = operation.register(params['name'], params['server'], with_depend=with_depend)
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
        operation.remove_package(params['name'], cleanup=cleanup)
    except operation.OperationError as e:
        ret['result'] = False
        ret['detail'] = str(e)
    else:
        ret['result'] = True
        ret['name'] = params['name']
    return ret


@make_api(require=['name', 'number'], error_check=True)
def remove_build(params):
    ret = {}
    try:
        operation.remove_build(params['name'], int(params['number']))
        ret['result'] = True
        ret['name'] = params['name']
        ret['number'] = params['number']
    except operation.OperationError as e:
        ret['result'] = False
        ret['detail'] = str(e)
    return ret


@make_api(require=['name'], error_check=True)
def cleanup(params):
    ret = {}
    try:
        operation.cleanup(params['name'])
        ret['result'] = True
        ret['name'] = params['name']
    except operation.OperationError as e:
        ret['result'] = False
        ret['detail'] = str(e)
    return ret


@make_api(error_check=True)
def cleanup_all(_):
    ret = {}
    try:
        operation.cleanup_all()
        ret['result'] = True
    except operation.OperationError as e:
        ret['result'] = False
        ret['detail'] = str(e)
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


@make_api(optional=['only_update'])
def package_build_all(_, **kwargs):
    only_update = 'only_update' in kwargs and kwargs['only_update'] == 'true'
    if only_update:
        operation.build_update()
    else:
        operation.build_all()
    return {'result': True}


@make_api(require=['name'], error_check=True, status=404)
def package_install(params):
    ret = dict()
    try:
        operation.install(params['name'])
    except operation.OperationError as e:
        ret['result'] = False
        ret['detail'] = str(e)
    else:
        ret['result'] = True
        ret['name'] = params['name']
    return ret


@make_api(require=['name'])
def toggle_ignore(params):
    ret = dict()
    try:
        ret['ignore'] = operation.toggle_ignore(params['name'])
    except operation.OperationError as e:
        ret['result'] = False
        ret['detail'] = str(e)
    else:
        ret['result'] = True
        ret['name'] = params['name']
    return ret
