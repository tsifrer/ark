from pyramid.view import notfound_view_config, exception_view_config


@notfound_view_config(renderer='json')
def notfound(request):
    request.response.status = 404
    return {'success': False, 'error': 'Not Found'}


@exception_view_config(Exception, renderer='json')
def error_view(request):
    request.response.status = 500
    print(str(request.exception))  # TODO: exception logging
    return {'success': False, 'error': 'Internal Server Error'}
