from binascii import hexlify

from chain.crypto.objects.transaction import Transaction

# TODO: MOARD TESTS!!!
# TODO: Test specific transaction types


def test_serialize_correctly_serializes_transaction(
    dummy_transaction, dummy_transaction_hash
):
    transaction = Transaction.from_dict(dummy_transaction)
    serialized = transaction.serialize()
    assert serialized == dummy_transaction_hash


def test_get_bytes_returns_correct_data():
    data = {
        "type": 0,
        "amount": 1000,
        "fee": 2000,
        "recipientId": "AJWRd23HNEhPLkK1ymMnwnDBX2a7QBZqff",
        "timestamp": 141738,
        "asset": {},
        "senderPublicKey": (
            "5d036a858ce89f844491762eb89e2bfbd50a4a0a0da658e4b2628b25b117ae09"
        ),
        "signature": (
            "618a54975212ead93df8c881655c625544bce8ed7ccdfe6f08a42eecfb1adebd051307be50"
            "14bb051617baf7815d50f62129e70918190361e5d4dd4796541b0a"
        ),
        "id": "13987348420913138422",
    }

    transaction = Transaction.from_dict(data)
    bytes_data = transaction.get_bytes()
    assert isinstance(bytes_data, bytes)
    assert len(bytes_data) == 202
    assert hexlify(bytes_data) == (
        b"00aa2902005d036a858ce89f844491762eb89e2bfbd50a4a0a0da658e4b2628b25b117ae09171"
        b"dfc69b54c7fe901e91d5a9ab78388645e2427ea00000000000000000000000000000000000000"
        b"00000000000000000000000000000000000000000000000000000000000000000000000000000"
        b"0000000000000e803000000000000d007000000000000618a54975212ead93df8c881655c6255"
        b"44bce8ed7ccdfe6f08a42eecfb1adebd051307be5014bb051617baf7815d50f62129e70918190"
        b"361e5d4dd4796541b0a"
    )


def test_from_serialized_correctly_deserializes_full_data(dummy_transaction_hash):
    transaction = Transaction.from_serialized(dummy_transaction_hash)

    assert transaction.version == 1
    assert transaction.network == 30
    assert transaction.type == 0
    assert transaction.timestamp == 24760418
    assert (
        transaction.sender_public_key
        == "0265c1f6b8c1966a90f3fed7bc32fd4f42238ab4938fdb2a4e7ddd01ae8b58b4c0"
    )
    assert transaction.fee == 10000000
    assert transaction.amount == 555760
    assert transaction.expiration == 0
    assert transaction.recipient_id == "DB4gFuDztmdGALMb8i1U4Z4R5SktxpNTAY"
    assert transaction.asset == {}
    assert transaction.vendor_field == "Goose Voter - True Block Weight"
    assert (
        transaction.vendor_field_hex
        == b"476f6f736520566f746572202d205472756520426c6f636b20576569676874"
    )
    assert (
        transaction.id
        == "170543154a3b79459cbaa529f9f62b6f1342682799eb549dbf09fcca2d1f9c11"
    )
    assert transaction.signature == (
        "304402204f12469157b19edd06ba25fcad3d4a5ef5b057c23f9e02de4641e6f8eef0553e022010"
        "121ab282f83efe1043de9c16bbf2c6845a03684229a0d7c965ffb9abdfb978"
    )
    assert transaction.second_signature == (
        "30450221008327862f0b9178d6665f7d6674978c5caf749649558d814244b1c66cdf945c400220"
        "15918134ef01fed3fe2a2efde3327917731344332724522c75c2799a14f78717"
    )
    assert transaction.sign_signature == (
        "30450221008327862f0b9178d6665f7d6674978c5caf749649558d814244b1c66cdf945c400220"
        "15918134ef01fed3fe2a2efde3327917731344332724522c75c2799a14f78717"
    )
    assert transaction.signatures is None
    assert transaction.block_id is None
    assert transaction.sequence == 0
    assert transaction.timelock is None
    assert transaction.timelock_type is None
    assert transaction.ipfs_hash is None
    assert transaction.payments is None


def test_from_dict_correctly_sets_data(dummy_transaction):
    transaction = Transaction.from_dict(dummy_transaction)
    assert transaction.version is None
    assert transaction.network is None
    assert transaction.type == 0
    assert transaction.timestamp == 24760418
    assert (
        transaction.sender_public_key
        == "0265c1f6b8c1966a90f3fed7bc32fd4f42238ab4938fdb2a4e7ddd01ae8b58b4c0"
    )
    assert transaction.fee == 10000000
    assert transaction.amount == 555760
    assert transaction.expiration is None
    assert transaction.recipient_id == "DB4gFuDztmdGALMb8i1U4Z4R5SktxpNTAY"
    assert transaction.asset == {}
    assert transaction.vendor_field == "Goose Voter - True Block Weight"
    assert transaction.vendor_field_hex is None
    assert (
        transaction.id
        == "1e5f0d734413f665cb5a859068cff1bccedcda9cc6df7e586ef61ba8fd74ef5d"
    )
    assert transaction.signature == (
        "304402204f12469157b19edd06ba25fcad3d4a5ef5b057c23f9e02de4641e6f8eef0553e022010"
        "121ab282f83efe1043de9c16bbf2c6845a03684229a0d7c965ffb9abdfb978"
    )
    assert transaction.second_signature is None
    assert transaction.sign_signature == (
        "30450221008327862f0b9178d6665f7d6674978c5caf749649558d814244b1c66cdf945c400220"
        "15918134ef01fed3fe2a2efde3327917731344332724522c75c2799a14f78717"
    )
    assert transaction.signatures is None
    assert transaction.block_id == "7176646138626297930"
    assert transaction.sequence == 0
    assert transaction.timelock is None
    assert transaction.timelock_type is None
    assert transaction.ipfs_hash is None
    assert transaction.payments is None


def test_verify_correctly_verifies_the_transaction():
    data = {
        "version": 1,
        "network": 30,
        "type": 0,
        "timestamp": 45021209,
        "senderPublicKey": (
            "03d3fdad9c5b25bf8880e6b519eb3611a5c0b31adebc8455f0e096175b28321aff"
        ),
        "fee": 10000000,
        "amount": 5100000000,
        "expiration": 0,
        "recipientId": "D8vKwaX6ksU3mWg7tJDm7v1dbxy4cMo4dh",
        "signature": (
            "3045022100f6914de508a19326148f3774456508270607fc2bee6c56acb2f7e2eb6999179c"
            "022043f9005f7d254bb0ecff2a14b035fc8aa83bd0e55135ff8c3181993606f2efe5"
        ),
        "id": "35904cf41b4df8f2e45d1aac366eca8fce25118d19b94333502cc66973adc815",
        "blockId": "10172429794310518146",
    }
    transaction = Transaction.from_dict(data)
    assert transaction.verify() is True
