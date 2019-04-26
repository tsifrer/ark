from chain.crypto import slots, time

from tests.chain.factories import WalletRedisFactory


DEFAULT_HEADERS = {"version": "2.0.0", "nethash": "asdfas", "port": 4003}


def test_sataus_returns_correct_response(p2p_service):
    response = p2p_service.get("/peer/status", headers=DEFAULT_HEADERS)
    assert response.status_code == 200
    assert response.json["success"] is True
    assert response.json["currentSlot"] == slots.get_slot_number(1, time.get_time())
    assert response.json["forgingAllowed"] == slots.is_forging_allowed(
        1, time.get_time()
    )
    assert response.json["height"] == 1
    assert response.json["header"] == {
        "blockSignature": (
            "3045022100b0cbfdfabb77b7d431cb7fdc3acd148032898eb6b0026d4e8f6f08f8e5ca23b5"
            "022044cfad1c8e0df615b0969c5d1fe4965b2c18e6656becc2d5410c68ed19452770"
        ),
        "generatorPublicKey": (
            "03d04acca0ad922998d258438cc453ce50222b0e761ae9a499ead6a11f3a44b70b"
        ),
        "height": 1,
        "id": "4881670189836572019",
        "idHex": "43bf2d2c67d29573",
        "numberOfTransactions": 255,
        "payloadHash": (
            "a63b5a3858afbca23edefac885be74d59f1a26985548a4082f4f479e74fcc348"
        ),
        "payloadLength": 55608,
        "previousBlock": None,
        "previousBlockHex": None,
        "reward": "0",
        "timestamp": 0,
        "totalAmount": "153000000000000",
        "totalFee": "0",
        "version": 0,
    }


def test_transactions_post_request(p2p_service, redis):
    WalletRedisFactory(
        redis,
        public_key="034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498",
        balance=1000000000,
    )

    post_data = {
        "transactions": [
            {
                "amount": 300000000,
                "fee": 342000,
                "id": (
                    "1774e2d8cb6f82498e626c804c04d8afac65cf5c110161fa39e9a5e6d6ce381b"
                ),
                "recipientId": "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof",
                "senderPublicKey": (
                    "034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498"
                ),
                "signature": (
                    "3044022007990057ef3696283be37f434313589879cb72eea62785354a0cd0a9d2"
                    "47c83702206da31cdeb06e33857e79ba4ff07292fc6c518125440ed264496fafd8"
                    "17ae6250"
                ),
                "timestamp": 66075124,
                "type": 0,
                "vendorField": "Spongebob Squarepants",
            }
        ]
    }
    response = p2p_service.post(
        "/peer/transactions", headers=DEFAULT_HEADERS, json=post_data
    )
    assert response.status_code == 200
    assert response.json["success"] is True
    assert response.json["transactionIds"] == [
        "1774e2d8cb6f82498e626c804c04d8afac65cf5c110161fa39e9a5e6d6ce381b"
    ]
