import json
from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='hello', renderer='json')
def hello_world(request):
    print('Incoming request')
    return {'foo': 'bar'}# Response('<body><h1>Hello World 1234!</h1></body>')

# def network_state_view():
    # TODO
    # abort(404)


# def blockchain_sync_view():
    # TODO
    # abort(404)




# @view_config(route_name='home')
# def blocks_view():
#     if not request.json:
#         print('wakanda')
#         abort(400)
#     print(request.json)
#     return json.dumps(request.json)
