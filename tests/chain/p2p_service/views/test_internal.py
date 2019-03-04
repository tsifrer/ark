def test_bla(p2p_service, dummy_block):
    response = p2p_service.post_json('/blocks', dummy_block)

    assert response.status_code == 204
