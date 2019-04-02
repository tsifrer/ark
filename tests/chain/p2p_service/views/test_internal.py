def test_bla(p2p_service, dummy_block):
    data = {
        "block": {
            "version": 0,
            "timestamp": 61694578,
            "height": 1691414,
            "previousBlockHex": "6bf024e51de4a549",
            "previousBlock": "7777757122936481097",
            "numberOfTransactions": 0,
            "totalAmount": 0,
            "totalFee": 0,
            "reward": 200000000,
            "payloadLength": 0,
            "payloadHash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "generatorPublicKey": "0239cb9bccb78ee5f66d6320c453ba65914a2da733856f029d818628ec0652075d",
            "blockSignature": "304402204f0889d13a40f460dda7944184dd7174f2c639570991f80e27a5e7ce6efaa98802205472cd0166d6633d86a07955834a45194464cfc7dc4cf4a3d876dba2626a76d8",
            "idHex": "30584879293d5fd7",
            "id": "3483613996991209431",
            "transactions": [],
            "ip": "158.69.181.17",
        }
    }

    response = p2p_service.post_json("/blocks", data)

    assert response.status_code == 204
