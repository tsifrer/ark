from chain.crypto.models.block import Block

# TODO: MOARD TESTS!!!


def test_serialize_full_correctly_serializes_block_and_its_transactions(
    dummy_block, dummy_block_full_hash
):
    block = Block(dummy_block)
    serialized = block.serialize_full()
    assert serialized == dummy_block_full_hash


def test_serialize_correctly_serializes_just_the_block(dummy_block, dummy_block_hash):
    block = Block(dummy_block)
    serialized = block.serialize()
    assert serialized == dummy_block_hash


# def test_creating_a_block_from_hex_header_only_correctly_sets_all_attributes(
#     dummy_block_hash
# ):
#     block = Block(dummy_block_hash)
#     assert block.version == 0
#     assert block.timestamp == 24760440
#     assert block.height == 2243161
#     assert block.previous_block_hex == b'2b324b8b33a85802'
#     assert block.previous_block == 3112633353705641986
#     assert block.number_of_transactions == 7
#     assert block.total_amount == 3890300
#     assert block.total_fee == 70000000
#     assert block.reward == 200000000
#     assert block.payload_length == 224
#     assert block.payload_hash == (
#         b'3784b953afcf936bdffd43fdf005b5732b49c1fc6b11e195c364c20b2eb06282'
#     )
#     assert block.generator_public_key == (
#         b'020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325'
#     )
#     assert block.block_signature == (
#         b'3045022100eee6c37b5e592e99811d588532726353592923f347c701d52912e6d583443e40022'
#         b'0277ffe38ad31e216ba0907c4738fed19b2071246b150c72c0a52bae4477ebe29'
#     )
#     assert block.id == 7176646138626297930
#     assert block.id_hex == b'639891a3bb7fd04a'
#     assert getattr(block, 'transactions', None) is None


def test_creating_a_block_from_hex_sets_all_attributes_including_transactions(
    dummy_block, dummy_block_full_hash
):
    block = Block(dummy_block_full_hash)
    assert block.version == 0
    assert block.timestamp == 24760440
    assert block.height == 2243161
    assert block.previous_block_hex == b'2b324b8b33a85802'
    assert block.previous_block == 3112633353705641986
    assert block.number_of_transactions == 7
    assert block.total_amount == 3890300
    assert block.total_fee == 70000000
    assert block.reward == 200000000
    assert block.payload_length == 224
    assert block.payload_hash == (
        b'3784b953afcf936bdffd43fdf005b5732b49c1fc6b11e195c364c20b2eb06282'
    )
    assert block.generator_public_key == (
        b'020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325'
    )
    assert block.block_signature == (
        b'3045022100eee6c37b5e592e99811d588532726353592923f347c701d52912e6d583443e40022'
        b'0277ffe38ad31e216ba0907c4738fed19b2071246b150c72c0a52bae4477ebe29'
    )
    assert block.id == 7176646138626297930
    assert block.id_hex == b'639891a3bb7fd04a'
    assert len(block.transactions) == 7

    for transaction, expected in zip(block.transactions, dummy_block['transactions']):
        assert transaction.version == 1
        assert transaction.network == 30
        assert transaction.type == expected['type']
        assert transaction.timestamp == expected['timestamp']
        assert transaction.sender_public_key == expected['senderPublicKey'].encode(
            'utf-8'
        )
        assert transaction.fee == expected['fee']
        assert transaction.amount == expected['amount']
        assert transaction.asset == expected['asset']


def test_get_id_hex_returns_correct_hex(dummy_block):
    block = Block(dummy_block)
    assert block.get_id_hex() == b'639891a3bb7fd04a'


def test_get_id_returns_correct_id(dummy_block):
    block = Block(dummy_block)
    assert block.get_id() == 7176646138626297930
