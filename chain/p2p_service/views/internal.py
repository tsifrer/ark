import json
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPMethodNotAllowed
from chain.crypto import slots
from chain.crypto.models.block import Block


@view_config(route_name='block_store', renderer='json')
def block_store_view(request):
    if request.method != 'POST':
        raise HTTPMethodNotAllowed(request.method)

    # TODO: Validate request data that it's correct block structure

    block = Block(request.json)
    print('Received new block at height {} with {} transactions, from {}'.format(
        block.height,
        block.number_of_transactions,
        request.remote_addr  # TODO: check if this works?
    ))
