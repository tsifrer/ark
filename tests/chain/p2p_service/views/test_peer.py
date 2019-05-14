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
            "304402202fe5de5697fa25d3d3c0cb24617ac02ddfb1c915ee9194a89f8392f948c6076402"
            "200d07c5244642fe36afa53fb2d048735f1adfa623e8fa4760487e5f72e17d253b"
        ),
        "generatorPublicKey": (
            "03b47f6b6719c76bad46a302d9cff7be9b1c2b2a20602a0d880f139b5b8901f068"
        ),
        "height": 1,
        "id": "17184958558311101492",
        "idHex": "ee7d3cc24bf13434",
        "numberOfTransactions": 153,
        "payloadHash": (
            "d9acd04bde4234a81addb8482333b4ac906bed7be5a9970ce8ada428bd083192"
        ),
        "payloadLength": 35960,
        "previousBlock": None,
        "previousBlockHex": None,
        "reward": "0",
        "timestamp": 0,
        "totalAmount": "12500000000000000",
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
