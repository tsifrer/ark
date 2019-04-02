import pytest


def test_requests_without_headers_are_rejected(p2p_service):
    response = p2p_service.get('/peer/status')
    assert response.status_code == 400
    assert response.json == {
        'errors': [
            'Missing version in request header',
            'Missing nethash in request header',
            'Missing port in request header',
        ],
        'message': 'Missing request headers',
        'status_code': 400,
    }


@pytest.mark.parametrize('key', [('version'), ('nethash'), ('port')])
def test_request_with_missing_header_is_rejected(key, p2p_service):
    headers = {'version': '2.0.0', 'nethash': 'asdfas', 'port': 4003}
    del headers[key]

    response = p2p_service.get('/peer/status', headers=headers)
    assert response.status_code == 400
    assert response.json == {
        'errors': ['Missing {} in request header'.format(key)],
        'message': 'Missing request headers',
        'status_code': 400,
    }


# # TODO: uncomment this once config endpoints are implemented
# def test_requests_to_config_endpoints_do_not_need_headers(p2p_service):
#     response = p2p_service.get('/config')
#     assert response.status_code == 200
