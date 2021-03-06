from copy import deepcopy

import pytest

from chain.crypto.objects.block import Block


# TODO: MOARD TESTS!!!
# def test_block_sets_default_values():
#     block = Block(version=1, timestamp=24760440, height=12345)
#     assert block.version == 1
#     assert block.timestamp == 24760440
#     assert block.height == 12345
#     assert block.previous_block_hex is None
#     assert block.previous_block is None
#     assert block.number_of_transactions == 0
#     assert block.total_amount == 0
#     assert block.total_fee == 0
#     assert block.reward == 0
#     assert block.payload_length == 0
#     assert block.payload_hash is None
#     assert block.generator_public_key is None
#     assert block.block_signature is None
#     assert block.id is None
#     assert block.id_hex is None
#     assert block.transactions == []


@pytest.mark.parametrize(
    "value,expected",
    [
        (1, b"0000000000000001"),
        (1337, b"0000000000000539"),
        (18043690079923428188, b"fa68108733135b5c"),
    ],
)
def test_to_bytes_hex_returns_correct_hex_value(value, expected):
    result = Block.to_bytes_hex(value)
    assert result == expected


def test_serialize_full_correctly_serializes_block_and_its_transactions(
    crypto_block, dummy_block_full_hash
):
    serialized = crypto_block.serialize_full()
    assert serialized == dummy_block_full_hash


def test_serialize_correctly_serializes_just_the_block(crypto_block, dummy_block_hash):
    serialized = crypto_block.serialize()
    assert serialized == dummy_block_hash


def test_from_serialized_correctly_sets_deserialized_types(
    dummy_block_hash, dummy_block
):
    block = Block.from_serialized(dummy_block_hash)

    assert isinstance(block.version, int)
    assert isinstance(block.timestamp, int)
    assert isinstance(block.height, int)
    assert isinstance(block.previous_block_hex, bytes)
    assert isinstance(block.previous_block, str)
    assert isinstance(block.number_of_transactions, int)
    assert isinstance(block.total_amount, int)
    assert isinstance(block.total_fee, int)
    assert isinstance(block.reward, int)
    assert isinstance(block.payload_length, int)
    assert isinstance(block.payload_hash, str)
    assert isinstance(block.generator_public_key, str)
    assert isinstance(block.block_signature, str)
    assert isinstance(block.id, str)
    assert isinstance(block.id_hex, bytes)
    assert isinstance(block.transactions, list)


def test_from_serialized_correctly_deserializes_full_data(
    dummy_block_full_hash, dummy_block
):
    block = Block.from_serialized(dummy_block_full_hash)
    assert block.version == 0
    assert block.timestamp == 24760440
    assert block.height == 2243161
    assert block.previous_block_hex == b"2b324b8b33a85802"
    assert block.previous_block == "3112633353705641986"
    assert block.number_of_transactions == 2
    assert block.total_amount == 3890300
    assert block.total_fee == 70000000
    assert block.reward == 200000000
    assert block.payload_length == 224
    assert block.payload_hash == (
        "3784b953afcf936bdffd43fdf005b5732b49c1fc6b11e195c364c20b2eb06282"
    )
    assert block.generator_public_key == (
        "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
    )
    assert block.block_signature == (
        "3045022100eee6c37b5e592e99811d588532726353592923f347c701d52912e6d583443e40022"
        "0277ffe38ad31e216ba0907c4738fed19b2071246b150c72c0a52bae4477ebe29"
    )
    assert block.id == "10977713934532967004"
    assert block.id_hex == b"9858aca939b17a5c"
    assert block.transactions is not None
    assert len(block.transactions) == 2
    for transaction, expected in zip(block.transactions, dummy_block["transactions"]):
        assert transaction.version == 1
        assert transaction.network == 23
        assert transaction.type == expected["type"]
        assert transaction.timestamp == expected["timestamp"]
        assert transaction.sender_public_key == expected["senderPublicKey"]
        assert transaction.fee == expected["fee"]
        assert transaction.amount == expected["amount"]
        assert transaction.asset == expected["asset"]


def test_from_dict_correctly_sets_data(dummy_block):
    block = Block.from_dict(dummy_block)

    assert block.version == 0
    assert block.timestamp == 24760440
    assert block.height == 2243161
    assert block.previous_block_hex == b"2b324b8b33a85802"
    assert block.previous_block == "3112633353705641986"
    assert block.number_of_transactions == 2
    assert block.total_amount == 3890300
    assert block.total_fee == 70000000
    assert block.reward == 200000000
    assert block.payload_length == 224
    assert block.payload_hash == (
        "3784b953afcf936bdffd43fdf005b5732b49c1fc6b11e195c364c20b2eb06282"
    )
    assert block.generator_public_key == (
        "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
    )
    assert block.block_signature == (
        "3045022100eee6c37b5e592e99811d588532726353592923f347c701d52912e6d583443e40022"
        "0277ffe38ad31e216ba0907c4738fed19b2071246b150c72c0a52bae4477ebe29"
    )
    assert block.id == "10977713934532967004"
    assert block.id_hex == b"9858aca939b17a5c"
    assert block.transactions is not None
    assert len(block.transactions) == 2
    for transaction, expected in zip(block.transactions, dummy_block["transactions"]):
        assert transaction.version is None
        assert transaction.network is None
        assert transaction.type == expected["type"]
        assert transaction.timestamp == expected["timestamp"]
        assert transaction.sender_public_key == expected["senderPublicKey"]
        assert transaction.fee == expected["fee"]
        assert transaction.amount == expected["amount"]
        assert transaction.asset == expected["asset"]
        assert transaction.vendor_field == expected["vendorField"]


def test_from_dict_raises_exception_for_wrong_type(dummy_block):
    data = deepcopy(dummy_block)
    data["id"] = float(data["id"])
    with pytest.raises(TypeError) as excinfo:
        Block.from_dict(data)
    assert str(excinfo.value) == (
        "Attribute id (<class 'float'>) must be of type (<class 'str'>, <class 'bytes'>"
        ")"
    )


def test_from_object_correctly_sets_data():
    # TODO:
    pass
