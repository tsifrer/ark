from chain.crypto import slots, time

DEFAULT_HEADERS = {
    'version': '2.0.0',
    'nethash': 'asdfas',
    'port': 4003,
}

# def test_bla(p2p_service, dummy_block):
#     data = {
#         "block": {
#             "version": 0,
#             "timestamp": 61694578,
#             "height": 1691414,
#             "previousBlockHex": "6bf024e51de4a549",
#             "previousBlock": "7777757122936481097",
#             "numberOfTransactions": 0,
#             "totalAmount": 0,
#             "totalFee": 0,
#             "reward": 200000000,
#             "payloadLength": 0,
#             "payloadHash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
#             "generatorPublicKey": "0239cb9bccb78ee5f66d6320c453ba65914a2da733856f029d818628ec0652075d",
#             "blockSignature": "304402204f0889d13a40f460dda7944184dd7174f2c639570991f80e27a5e7ce6efaa98802205472cd0166d6633d86a07955834a45194464cfc7dc4cf4a3d876dba2626a76d8",
#             "idHex": "30584879293d5fd7",
#             "id": "3483613996991209431",
#             "transactions": [],
#             "ip": "158.69.181.17",
#         }
#     }

#     response = p2p_service.post('/peer/blocks', json=data)
#     assert response.status_code == 200
#     assert response.json['success'] is True


def test_sataus_returns_correct_response(p2p_service):
    response = p2p_service.get('/peer/status', headers=DEFAULT_HEADERS)
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['currentSlot'] == slots.get_slot_number(1, time.get_time())
    assert response.json['forgingAllowed'] == slots.is_forging_allowed(1, time.get_time())
    assert response.json['height'] == 1
    assert response.json['header'] == {
        'blockSignature': '3045022100b0cbfdfabb77b7d431cb7fdc3acd148032898eb6b0026d4e8f6f08f8e5ca23b5022044cfad1c8e0df615b0969c5d1fe4965b2c18e6656becc2d5410c68ed19452770',
        'generatorPublicKey': '03d04acca0ad922998d258438cc453ce50222b0e761ae9a499ead6a11f3a44b70b',
        'height': 1,
        'id': '4881670189836572019',
        'idHex': '43bf2d2c67d29573',
        'numberOfTransactions': 255,
        'payloadHash': 'a63b5a3858afbca23edefac885be74d59f1a26985548a4082f4f479e74fcc348',
        'payloadLength': 55608,
        'previousBlock': None,
        'previousBlockHex': None,
        'reward': '0',
        'timestamp': 0,
        'totalAmount': '153000000000000',
        'totalFee': '0',
        'version': 0
    }
