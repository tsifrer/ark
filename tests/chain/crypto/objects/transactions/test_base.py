import pytest

from chain.crypto.bytebuffer import ByteBuffer
from chain.crypto.constants import (
    TRANSACTION_TYPE_DELEGATE_REGISTRATION,
    TRANSACTION_TYPE_DELEGATE_RESIGNATION,
    TRANSACTION_TYPE_IPFS,
    TRANSACTION_TYPE_MULTI_PAYMENT,
    TRANSACTION_TYPE_MULTI_SIGNATURE,
    TRANSACTION_TYPE_SECOND_SIGNATURE,
    TRANSACTION_TYPE_TIMELOCK_TRANSFER,
    TRANSACTION_TYPE_TRANSFER,
    TRANSACTION_TYPE_VOTE,
)
from chain.crypto.models.wallet import Wallet
from chain.crypto.objects.transactions.base import BaseTransaction


def test_from_dict(dummy_transaction):
    transaction = BaseTransaction.from_dict(dummy_transaction)
    assert transaction.version is None
    assert transaction.network is None
    assert transaction.type == 0
    assert transaction.timestamp == 67048949
    assert (
        transaction.sender_public_key
        == "034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498"
    )
    assert transaction.fee == 342000
    assert transaction.amount == 100000000
    assert transaction.expiration is None
    assert transaction.recipient_id == "AFnw7orqn9B4HBKrKawJgfn5dvoL7zr38B"
    assert transaction.asset == {}
    assert transaction.vendor_field == "Patrick Star"
    assert transaction.signature == (
        "3045022100f0e49ea11b99410ecb3a3b449659496f934ab5af8028701108f4df41c8e1feac0220"
        "5c2cfd5e7c11d6dd8b206e631a445f676f8b23ea0ccc74bc802eb03abbec8092"
    )
    assert transaction.second_signature is None
    assert transaction.sign_signature is None
    assert transaction.signatures == []
    assert transaction.block_id is None
    assert transaction.sequence == 0
    assert transaction.timelock is None
    assert transaction.timelock_type is None
    assert transaction.ipfs_hash is None
    assert transaction.payments is None
    assert (
        transaction.id
        == "f861b25c9a87fc8913282da8855ee63b9cbaa9324543377a5bdfc5afccb92aaa"
    )


@pytest.mark.parametrize("data", [123, [], "harambe", b"harambe"])
def test_from_dict_raises_type_error_if_data_is_not_dict(data):
    with pytest.raises(TypeError) as excinfo:
        BaseTransaction.from_dict(data)
    assert str(excinfo.value) == "data must be dict"


def test_from_dict_raises_value_error_if_field_is_required(dummy_transaction):
    del dummy_transaction["timestamp"]
    with pytest.raises(ValueError) as excinfo:
        BaseTransaction.from_dict(dummy_transaction)
    assert str(excinfo.value) == "Attribute timestamp is required"


def test_from_dict_raises_type_error_if_value_invalid_type(dummy_transaction):
    dummy_transaction["vendorField"] = 1234
    with pytest.raises(TypeError) as excinfo:
        BaseTransaction.from_dict(dummy_transaction)
    assert str(excinfo.value) == (
        "Attribute vendor_field (<class 'int'>) must be of type (<class 'str'>, "
        "<class 'bytes'>)"
    )


def test_from_serialized(dummy_transaction_hash):
    transaction = BaseTransaction.from_serialized(dummy_transaction_hash)

    assert transaction.version == 1
    assert transaction.network == 23
    assert transaction.type == 0
    assert transaction.timestamp == 67048949
    assert (
        transaction.sender_public_key
        == "034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498"
    )
    assert transaction.fee == 342000
    assert transaction.amount == 100000000
    assert transaction.expiration == 0
    assert transaction.recipient_id == "AFnw7orqn9B4HBKrKawJgfn5dvoL7zr38B"
    assert transaction.asset == {}
    assert transaction.vendor_field == "Patrick Star"
    assert transaction.signature == (
        "3045022100f0e49ea11b99410ecb3a3b449659496f934ab5af8028701108f4df41c8e1feac0220"
        "5c2cfd5e7c11d6dd8b206e631a445f676f8b23ea0ccc74bc802eb03abbec8092"
    )
    assert transaction.second_signature is None
    assert transaction.sign_signature is None
    assert transaction.signatures == []
    assert transaction.block_id is None
    assert transaction.sequence == 0
    assert transaction.timelock is None
    assert transaction.timelock_type is None
    assert transaction.ipfs_hash is None
    assert transaction.payments is None
    assert (
        transaction.id
        == "f861b25c9a87fc8913282da8855ee63b9cbaa9324543377a5bdfc5afccb92aaa"
    )


@pytest.mark.parametrize("data", [123, [], "harambe"])
def test_from_serialized_raises_type_error_if_data_is_not_dict(data):
    with pytest.raises(TypeError) as excinfo:
        BaseTransaction.from_serialized(data)
    assert str(excinfo.value) == "bytes_string must be bytes"


def test_from_object(crypto_transaction):
    transaction = BaseTransaction.from_object(crypto_transaction)

    assert transaction.version is None
    assert transaction.network is None
    assert transaction.type == 0
    assert transaction.timestamp == 67048949
    assert (
        transaction.sender_public_key
        == "034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498"
    )
    assert transaction.fee == 342000
    assert transaction.amount == 100000000
    assert transaction.expiration == 0
    assert transaction.recipient_id == "AFnw7orqn9B4HBKrKawJgfn5dvoL7zr38B"
    assert transaction.asset == {}
    assert transaction.vendor_field == "Patrick Star"
    assert transaction.signature == (
        "3045022100f0e49ea11b99410ecb3a3b449659496f934ab5af8028701108f4df41c8e1feac0220"
        "5c2cfd5e7c11d6dd8b206e631a445f676f8b23ea0ccc74bc802eb03abbec8092"
    )
    assert transaction.second_signature is None
    assert transaction.sign_signature is None
    assert transaction.signatures == []
    assert transaction.block_id is None
    assert transaction.sequence == 0
    assert transaction.timelock is None
    assert transaction.timelock_type is None
    assert transaction.ipfs_hash is None
    assert transaction.payments is None
    assert (
        transaction.id
        == "f861b25c9a87fc8913282da8855ee63b9cbaa9324543377a5bdfc5afccb92aaa"
    )


def test_from_object_raises_for_required_fields(crypto_transaction):
    crypto_transaction.timestamp = None
    with pytest.raises(ValueError) as excinfo:
        BaseTransaction.from_object(crypto_transaction)
    assert str(excinfo.value) == "Attribute timestamp is required"


def test_from_object_raises_for_wrong_field_type(crypto_transaction):
    crypto_transaction.vendor_field = 1234
    with pytest.raises(TypeError) as excinfo:
        BaseTransaction.from_object(crypto_transaction)
    assert str(excinfo.value) == (
        "Attribute vendor_field (<class 'int'>) must be of type (<class 'str'>, "
        "<class 'bytes'>)"
    )


def test_serialize_correctly_serializes_transaction(
    dummy_transaction_hash, crypto_transaction
):
    serialized = crypto_transaction.serialize()
    assert serialized == dummy_transaction_hash


@pytest.mark.parametrize(
    "transaction_type,expected",
    [
        (TRANSACTION_TYPE_DELEGATE_REGISTRATION, False),
        (TRANSACTION_TYPE_DELEGATE_RESIGNATION, False),
        (TRANSACTION_TYPE_IPFS, False),
        (TRANSACTION_TYPE_MULTI_PAYMENT, False),
        (TRANSACTION_TYPE_MULTI_SIGNATURE, False),
        (TRANSACTION_TYPE_SECOND_SIGNATURE, False),
        (TRANSACTION_TYPE_TIMELOCK_TRANSFER, True),
        (TRANSACTION_TYPE_TRANSFER, True),
        (TRANSACTION_TYPE_VOTE, False),
    ],
)
def test_can_have_vendor_field(transaction_type, expected):
    can_have = BaseTransaction.can_have_vendor_field(transaction_type)
    assert can_have == expected


@pytest.mark.parametrize(
    "vendor_field,transaction_type,expected",
    [
        ("Patrick Star", TRANSACTION_TYPE_TRANSFER, b"\x0cPatrick Star"),
        (None, TRANSACTION_TYPE_TRANSFER, b"\x00"),
        ("Patrick Star", TRANSACTION_TYPE_VOTE, b"\x00"),
        (None, TRANSACTION_TYPE_VOTE, b"\x00"),
        (
            "⊁⊁⊁",
            TRANSACTION_TYPE_TRANSFER,
            b"\t\xe2\x8a\x81\xe2\x8a\x81\xe2\x8a\x81",
        ),
    ],
)
def test_serialize_vendor_field(
    vendor_field, transaction_type, expected, crypto_transaction
):
    crypto_transaction.vendor_field = vendor_field
    crypto_transaction.type = transaction_type
    data = crypto_transaction._serialize_vendor_field()
    assert data == expected


def test_serialize_type_transfer(crypto_transaction):
    crypto_transaction.type = TRANSACTION_TYPE_TRANSFER
    crypto_transaction.amount = 1337
    crypto_transaction.expiration = 33
    crypto_transaction.recipient_id = "AS2YSSDbbXBAehfbm1KAEvJMJFdPPT2aRT"
    data = crypto_transaction._serialize_type()
    assert data == (
        b"9\x05\x00\x00\x00\x00\x00\x00!\x00\x00\x00\x17pwv\x97\xad\xc7mQW|\x83\xbf/"
        b"=\xfc\xb6z\xcb\xe3\x06"
    )


def test_serialize_type_second_signature(crypto_transaction):
    crypto_transaction.type = TRANSACTION_TYPE_SECOND_SIGNATURE
    crypto_transaction.asset["signature"] = {
        "publicKey": (
            "034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498"
        )
    }
    data = crypto_transaction._serialize_type()
    assert data == (
        b"\x03J\xff\xde\xe0\xef\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5\xb8\n\xdc\xcc\x84$E"
        b"\xa1\x87\xb2\xf8\x0f+\xb4\\r\xc4\x98"
    )


def test_serialize_type_delegate_registration(crypto_transaction):
    crypto_transaction.type = TRANSACTION_TYPE_DELEGATE_REGISTRATION
    crypto_transaction.asset["delegate"] = {"username": "harambe"}
    data = crypto_transaction._serialize_type()
    assert data == b"\x0eharambe"


@pytest.mark.parametrize(
    "votes,expected",
    [
        (
            ["+034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498"],
            b"\x01\x01\x03J\xff\xde\xe0\xef\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5\xb8\n\xdc"
            b"\xcc\x84$E\xa1\x87\xb2\xf8\x0f+\xb4\\r\xc4\x98",
        ),
        (
            ["-034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498"],
            b"\x01\x00\x03J\xff\xde\xe0\xef\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5\xb8\n\xdc"
            b"\xcc\x84$E\xa1\x87\xb2\xf8\x0f+\xb4\\r\xc4\x98",
        ),
        (
            [
                "-034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498",
                "+034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c721337",
            ],
            b"\x02\x00\x03J\xff\xde\xe0\xef\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5\xb8\n\xdc"
            b"\xcc\x84$E\xa1\x87\xb2\xf8\x0f+\xb4\\r\xc4\x98\x01\x03J\xff\xde\xe0\xef"
            b"\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5\xb8\n\xdc\xcc\x84$E\xa1\x87\xb2\xf8\x0f"
            b"+\xb4\\r\x137",
        ),
    ],
)
def test_serialize_type_vote(votes, expected, crypto_transaction):
    crypto_transaction.type = TRANSACTION_TYPE_VOTE
    crypto_transaction.asset["votes"] = votes

    data = crypto_transaction._serialize_type()
    assert data == expected


def test_serialize_type_multi_signature(crypto_transaction):
    crypto_transaction.type = TRANSACTION_TYPE_MULTI_SIGNATURE
    crypto_transaction.asset["multisignature"] = {
        "keysgroup": [
            "034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498",
            "+03e88b0c85ea85697c3db8fd6ea08bba896339ededff04439f48c54d36e2ff9853",
        ],
        "min": 5,
        "lifetime": 3,
    }
    data = crypto_transaction._serialize_type()
    assert len(data) < 200
    assert data == (
        b"\x05\x02\x03\x03J\xff\xde\xe0\xef\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5\xb8\n\xdc"
        b"\xcc\x84$E\xa1\x87\xb2\xf8\x0f+\xb4\\r\xc4\x98\x03\xe8\x8b\x0c\x85\xea\x85i|="
        b"\xb8\xfdn\xa0\x8b\xba\x89c9\xed\xed\xff\x04C\x9fH\xc5M6\xe2\xff\x98S"
    )


def test_serialize_type_ipfs(crypto_transaction):
    crypto_transaction.type = TRANSACTION_TYPE_IPFS
    crypto_transaction.asset["ipfs"] = {"dag": "da304502"}
    data = crypto_transaction._serialize_type()
    assert data == b"\x04\xda0E\x02"


def test_serialize_type_timelock_transfer(crypto_transaction):
    crypto_transaction.type = TRANSACTION_TYPE_TIMELOCK_TRANSFER
    crypto_transaction.timelock_type = 0
    crypto_transaction.timelock = 12
    crypto_transaction.amount = 1337
    crypto_transaction.recipient_id = "AS2YSSDbbXBAehfbm1KAEvJMJFdPPT2aRT"
    data = crypto_transaction._serialize_type()
    assert data == (
        b"9\x05\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x17pwv\x97"
        b"\xad\xc7mQW|\x83\xbf/=\xfc\xb6z\xcb\xe3\x06"
    )


def test_serialize_type_multi_payment(crypto_transaction):
    crypto_transaction.type = TRANSACTION_TYPE_MULTI_PAYMENT
    crypto_transaction.asset["payments"] = [
        {"amount": 1337, "recipientId": "AS2YSSDbbXBAehfbm1KAEvJMJFdPPT2aRT"},
        {"amount": 666, "recipientId": "AS2YSSDbbXBAehfbm1KAEvJMJFdPPT2aRT"},
    ]
    data = crypto_transaction._serialize_type()
    assert data == (
        b"\x02\x00\x00\x009\x05\x00\x00\x00\x00\x00\x00\x17pwv\x97\xad\xc7mQW|\x83\xbf"
        b"/=\xfc\xb6z\xcb\xe3\x06\x9a\x02\x00\x00\x00\x00\x00\x00\x17pwv\x97\xad\xc7mQ"
        b"W|\x83\xbf/=\xfc\xb6z\xcb\xe3\x06"
    )


def test_serialize_type_delegate_resignation(crypto_transaction):
    crypto_transaction.type = TRANSACTION_TYPE_DELEGATE_RESIGNATION
    data = crypto_transaction._serialize_type()
    assert data == b""


@pytest.mark.parametrize(
    "signature,second_signature,sign_signature,signatures,expected",
    [
        (False, False, False, False, b""),
        (
            True,
            False,
            False,
            False,
            (
                b"0E\x02!\x00\xf0\xe4\x9e\xa1\x1b\x99A\x0e\xcb:;D\x96YIo\x93J\xb5\xaf"
                b"\x80(p\x11\x08\xf4\xdfA\xc8\xe1\xfe\xac\x02 \\,\xfd^|\x11\xd6\xdd\x8b"
                b" nc\x1aD_go\x8b#\xea\x0c\xcct\xbc\x80.\xb0:\xbb\xec\x80\x92"
            ),
        ),
        (
            True,
            True,
            False,
            False,
            (
                b"0E\x02!\x00\xf0\xe4\x9e\xa1\x1b\x99A\x0e\xcb:;D\x96YIo\x93J\xb5\xaf"
                b"\x80(p\x11\x08\xf4\xdfA\xc8\xe1\xfe\xac\x02 \\,\xfd^|\x11\xd6\xdd\x8b"
                b" nc\x1aD_go\x8b#\xea\x0c\xcct\xbc\x80.\xb0:\xbb\xec\x80\x920E\x02!"
                b"\x00\xff\xf7\n\xdd\x8d\xb1\xd5M\x1cPL5D\x17\xc2\xbaZ\x03@\x1e\x93\xcd"
                b"\x9e\xc3\xf7V\x05\xa6H\x88\xd0E\x02 <p\xc1\xa8l<Aj\xf9\x13\xa4\xd6W"
                b'\xb4a\xd7?"\x97\x06\x18\x01\x98$c\xd7\xbdG\xf5\xa9\x1c\xfe'
            ),
        ),
        (
            True,
            True,
            True,
            False,
            (
                b"0E\x02!\x00\xf0\xe4\x9e\xa1\x1b\x99A\x0e\xcb:;D\x96YIo\x93J\xb5\xaf"
                b"\x80(p\x11\x08\xf4\xdfA\xc8\xe1\xfe\xac\x02 \\,\xfd^|\x11\xd6\xdd\x8b"
                b" nc\x1aD_go\x8b#\xea\x0c\xcct\xbc\x80.\xb0:\xbb\xec\x80\x920E\x02!"
                b"\x00\xff\xf7\n\xdd\x8d\xb1\xd5M\x1cPL5D\x17\xc2\xbaZ\x03@\x1e\x93\xcd"
                b"\x9e\xc3\xf7V\x05\xa6H\x88\xd0E\x02 <p\xc1\xa8l<Aj\xf9\x13\xa4\xd6W"
                b'\xb4a\xd7?"\x97\x06\x18\x01\x98$c\xd7\xbdG\xf5\xa9\x1c\xfe'
            ),
        ),
        (
            True,
            True,
            True,
            True,
            (
                b"0E\x02!\x00\xf0\xe4\x9e\xa1\x1b\x99A\x0e\xcb:;D\x96YIo\x93J\xb5\xaf"
                b"\x80(p\x11\x08\xf4\xdfA\xc8\xe1\xfe\xac\x02 \\,\xfd^|\x11\xd6\xdd\x8b"
                b" nc\x1aD_go\x8b#\xea\x0c\xcct\xbc\x80.\xb0:\xbb\xec\x80\x920E\x02!"
                b"\x00\xff\xf7\n\xdd\x8d\xb1\xd5M\x1cPL5D\x17\xc2\xbaZ\x03@\x1e\x93\xcd"
                b"\x9e\xc3\xf7V\x05\xa6H\x88\xd0E\x02 <p\xc1\xa8l<Aj\xf9\x13\xa4\xd6W"
                b'\xb4a\xd7?"\x97\x06\x18\x01\x98$c\xd7\xbdG\xf5\xa9\x1c\xfe\xff0E\x02!'
                b"\x00\xe1\xdf\xf5\xc0\xa4(\x9f\xfe\xe8\xca\xa7\x9f\xd2_\xe8o\r\xedM"
                b"\xaa\xeb\x9f%\xe1#\xea2{\x01\xfd\xb9q\x02 Gm\xa4\xd1we/\xe4\xa3u\xe4"
                b"\x14\x08\x9c\xe8\xc8h\x00\xbc\xc4\xcal\xe0\xb6\xd9t\xef\x98\xd8\xc9"
                b"\xd4\xcf0E\x02!\x00\xae\xf4\x82\xec\xae\xa6\xec\xaf\x8eo\x86\xbdz"
                b"\xc4tE\x8eev\x14\xb3\xeb\x9eD\x07\x89T\x9d\x1e\xa8_`\x02 \\uv4\x11"
                b'\xe0\xfe\xbb}\x11\xa7\xcc\xf7\xcb\x82o\xc1\x1d\xdb\xe3r+s\xf7~"\xe9'
                b"\xf0\x91\x9e\x17\x9d"
            ),
        ),
        (
            True,
            False,
            True,
            False,
            (
                b"0E\x02!\x00\xf0\xe4\x9e\xa1\x1b\x99A\x0e\xcb:;D\x96YIo\x93J\xb5\xaf"
                b"\x80(p\x11\x08\xf4\xdfA\xc8\xe1\xfe\xac\x02 \\,\xfd^|\x11\xd6\xdd\x8b"
                b" nc\x1aD_go\x8b#\xea\x0c\xcct\xbc\x80.\xb0:\xbb\xec\x80\x920D\x02 Y"
                b"\xab\x88\xd3\xfe\x83\xd6\xb5-\xdd^\x866\x96Aah\xf9\xca\xc6\xde\x96#hX"
                b"z\xd745B\xf9\x9f\x02 z\x95\xcaG0\x06\xabW\xde\xe6\xb0n\x06\xf8\xfa"
                b'\x8f\x1b&\x05H\xb9"f\x14\xa0\xe1\xf7`\xcc\x91\x04y'
            ),
        ),
        (False, False, True, False, b""),
        (False, True, False, False, b""),
        (False, False, True, True, b""),
        (False, True, False, True, b""),
        (
            True,
            False,
            False,
            True,
            (
                b"0E\x02!\x00\xf0\xe4\x9e\xa1\x1b\x99A\x0e\xcb:;D\x96YIo\x93J\xb5\xaf"
                b"\x80(p\x11\x08\xf4\xdfA\xc8\xe1\xfe\xac\x02 \\,\xfd^|\x11\xd6\xdd\x8b"
                b" nc\x1aD_go\x8b#\xea\x0c\xcct\xbc\x80.\xb0:\xbb\xec\x80\x92\xff0E\x02"
                b"!\x00\xe1\xdf\xf5\xc0\xa4(\x9f\xfe\xe8\xca\xa7\x9f\xd2_\xe8o\r\xedM"
                b"\xaa\xeb\x9f%\xe1#\xea2{\x01\xfd\xb9q\x02 Gm\xa4\xd1we/\xe4\xa3u\xe4"
                b"\x14\x08\x9c\xe8\xc8h\x00\xbc\xc4\xcal\xe0\xb6\xd9t\xef\x98\xd8\xc9"
                b"\xd4\xcf0E\x02!\x00\xae\xf4\x82\xec\xae\xa6\xec\xaf\x8eo\x86\xbdz\xc4"
                b"tE\x8eev\x14\xb3\xeb\x9eD\x07\x89T\x9d\x1e\xa8_`\x02 \\uv4\x11\xe0"
                b'\xfe\xbb}\x11\xa7\xcc\xf7\xcb\x82o\xc1\x1d\xdb\xe3r+s\xf7~"\xe9\xf0'
                b"\x91\x9e\x17\x9d"
            ),
        ),
    ],
)
def test_serialize_signatures(
    signature, second_signature, sign_signature, signatures, expected
):
    transaction = BaseTransaction()
    if signature:
        transaction.signature = (
            "3045022100f0e49ea11b99410ecb3a3b449659496f934ab5af8028701108f4df41c8e1feac"
            "02205c2cfd5e7c11d6dd8b206e631a445f676f8b23ea0ccc74bc802eb03abbec8092"
        )

    if second_signature:
        transaction.second_signature = (
            "3045022100fff70add8db1d54d1c504c354417c2ba5a03401e93cd9ec3f75605a64888d045"
            "02203c70c1a86c3c416af913a4d657b461d73f2297061801982463d7bd47f5a91cfe"
        )

    if sign_signature:
        transaction.sign_signature = (
            "3044022059ab88d3fe83d6b52ddd5e863696416168f9cac6de962368587ad7343542f99f02"
            "207a95ca473006ab57dee6b06e06f8fa8f1b260548b9226614a0e1f760cc910479"
        )

    if signatures:
        transaction.signatures = [
            (
                "3045022100e1dff5c0a4289ffee8caa79fd25fe86f0ded4daaeb9f25e123ea327b01fd"
                "b9710220476da4d177652fe4a375e414089ce8c86800bcc4ca6ce0b6d974ef98d8c9d4"
                "cf"
            ),
            (
                "3045022100aef482ecaea6ecaf8e6f86bd7ac474458e657614b3eb9e440789549d1ea8"
                "5f6002205c75763411e0febb7d11a7ccf7cb826fc11ddbe3722b73f77e22e9f0919e17"
                "9d"
            ),
        ]
    bytes_data = transaction._serialize_signatures()
    assert bytes_data == expected


def test_serialize(crypto_transaction, dummy_transaction_hash):
    serialized = crypto_transaction.serialize()
    assert serialized == dummy_transaction_hash


def test_deserialize_type():
    transaction = BaseTransaction()
    transaction.type = TRANSACTION_TYPE_TRANSFER
    buff = ByteBuffer(
        b"9\x05\x00\x00\x00\x00\x00\x00!\x00\x00\x00\x17pwv\x97\xad\xc7mQW|\x83\xbf/="
        b"\xfc\xb6z\xcb\xe3\x06"
    )
    transaction._deserialize_type(buff)
    assert transaction.amount == 1337
    assert transaction.expiration == 33
    assert transaction.recipient_id == "AS2YSSDbbXBAehfbm1KAEvJMJFdPPT2aRT"


def test_deserialize_type_transfer():
    transaction = BaseTransaction()
    transaction.type = TRANSACTION_TYPE_TRANSFER
    buff = ByteBuffer(
        b"9\x05\x00\x00\x00\x00\x00\x00!\x00\x00\x00\x17pwv\x97\xad\xc7mQW|\x83\xbf/="
        b"\xfc\xb6z\xcb\xe3\x06"
    )
    transaction._deserialize_type(buff)
    assert transaction.amount == 1337
    assert transaction.expiration == 33
    assert transaction.recipient_id == "AS2YSSDbbXBAehfbm1KAEvJMJFdPPT2aRT"


def test_deserialize_type_second_signature():
    transaction = BaseTransaction()
    transaction.type = TRANSACTION_TYPE_SECOND_SIGNATURE
    buff = ByteBuffer(
        b"\x03J\xff\xde\xe0\xef\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5\xb8\n\xdc\xcc\x84$E"
        b"\xa1\x87\xb2\xf8\x0f+\xb4\\r\xc4\x98"
    )
    transaction._deserialize_type(buff)
    assert transaction.asset == {
        "signature": {
            "publicKey": (
                "034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498"
            )
        }
    }


def test_deserialize_type_delegate_registraion():
    transaction = BaseTransaction()
    transaction.type = TRANSACTION_TYPE_DELEGATE_REGISTRATION
    buff = ByteBuffer(b"\x0eharambe")
    transaction._deserialize_type(buff)
    assert transaction.asset == {"delegate": {"username": "harambe"}}


@pytest.mark.parametrize(
    "bytes_data,expected",
    [
        (
            b"\x01\x01\x03J\xff\xde\xe0\xef\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5\xb8\n\xdc"
            b"\xcc\x84$E\xa1\x87\xb2\xf8\x0f+\xb4\\r\xc4\x98",
            ["+034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498"],
        ),
        (
            b"\x01\x00\x03J\xff\xde\xe0\xef\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5\xb8\n\xdc"
            b"\xcc\x84$E\xa1\x87\xb2\xf8\x0f+\xb4\\r\xc4\x98",
            ["-034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498"],
        ),
        (
            b"\x02\x00\x03J\xff\xde\xe0\xef\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5\xb8\n\xdc"
            b"\xcc\x84$E\xa1\x87\xb2\xf8\x0f+\xb4\\r\xc4\x98\x01\x03J\xff\xde\xe0\xef"
            b"\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5\xb8\n\xdc\xcc\x84$E\xa1\x87\xb2\xf8\x0f"
            b"+\xb4\\r\x137",
            [
                "-034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498",
                "+034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c721337",
            ],
        ),
    ],
)
def test_deserialize_type_vote(bytes_data, expected):
    transaction = BaseTransaction()
    transaction.type = TRANSACTION_TYPE_VOTE
    buff = ByteBuffer(bytes_data)
    transaction._deserialize_type(buff)
    assert transaction.asset == {"votes": expected}


def test_deserialize_type_multi_signature():
    transaction = BaseTransaction()
    transaction.type = TRANSACTION_TYPE_MULTI_SIGNATURE
    buff = ByteBuffer(
        b"\x05\x02\x03\x03J\xff\xde\xe0\xef\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5\xb8\n\xdc"
        b"\xcc\x84$E\xa1\x87\xb2\xf8\x0f+\xb4\\r\xc4\x98\x03\xe8\x8b\x0c\x85\xea\x85i"
        b"|=\xb8\xfdn\xa0\x8b\xba\x89c9\xed\xed\xff\x04C\x9fH\xc5M6\xe2\xff\x98S"
    )
    transaction._deserialize_type(buff)
    assert transaction.asset == {
        "multisignature": {
            "keysgroup": [
                "034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498",
                "03e88b0c85ea85697c3db8fd6ea08bba896339ededff04439f48c54d36e2ff9853",
            ],
            "min": 5,
            "lifetime": 3,
        }
    }


def test_deserialize_type_ipfs():
    transaction = BaseTransaction()
    transaction.type = TRANSACTION_TYPE_IPFS
    buff = ByteBuffer(b"\x04\xda0E\x02")
    transaction._deserialize_type(buff)
    assert transaction.asset == {"ipfs": {"dag": "da304502"}}


def test_deserialize_type_timelock_transfer():
    transaction = BaseTransaction()
    transaction.type = TRANSACTION_TYPE_TIMELOCK_TRANSFER
    buff = ByteBuffer(
        b"9\x05\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x17pwv\x97"
        b"\xad\xc7mQW|\x83\xbf/=\xfc\xb6z\xcb\xe3\x06"
    )
    transaction._deserialize_type(buff)
    assert transaction.timelock_type == 0
    assert transaction.timelock == 12
    assert transaction.amount == 1337
    assert transaction.recipient_id == "AS2YSSDbbXBAehfbm1KAEvJMJFdPPT2aRT"


def test_deserialize_type_multi_payment():
    transaction = BaseTransaction()
    transaction.type = TRANSACTION_TYPE_MULTI_PAYMENT
    buff = ByteBuffer(
        b"\x02\x00\x00\x009\x05\x00\x00\x00\x00\x00\x00\x17pwv\x97\xad\xc7mQW|\x83\xbf"
        b"/=\xfc\xb6z\xcb\xe3\x06\x9a\x02\x00\x00\x00\x00\x00\x00\x17pwv\x97\xad\xc7mQW"
        b"|\x83\xbf/=\xfc\xb6z\xcb\xe3\x06"
    )
    transaction._deserialize_type(buff)
    assert transaction.asset == {
        "payments": [
            {"amount": 1337, "recipientId": "AS2YSSDbbXBAehfbm1KAEvJMJFdPPT2aRT"},
            {"amount": 666, "recipientId": "AS2YSSDbbXBAehfbm1KAEvJMJFdPPT2aRT"},
        ]
    }
    assert transaction.amount == 2003


def test_deserialize_type_delegate_resignation():
    transaction = BaseTransaction()
    transaction.type = TRANSACTION_TYPE_DELEGATE_RESIGNATION
    buff = ByteBuffer(b"")
    # ATM this shouldn't do anything so just check that it doesn't raise an error
    transaction._deserialize_type(buff)


def test_deserialize_type_raises_for_invalid_trnasaction_type():
    transaction = BaseTransaction()
    transaction.type = 123
    buff = ByteBuffer(b"")
    with pytest.raises(Exception) as excinfo:
        transaction._deserialize_type(buff)
    assert str(excinfo.value) == "Transaction type is invalid"


@pytest.mark.parametrize(
    "signature,second_signature,sign_signature,signatures,bytes_data",
    [
        (False, False, False, False, b""),
        (
            True,
            False,
            False,
            False,
            (
                b"0E\x02!\x00\xf0\xe4\x9e\xa1\x1b\x99A\x0e\xcb:;D\x96YIo\x93J\xb5\xaf"
                b"\x80(p\x11\x08\xf4\xdfA\xc8\xe1\xfe\xac\x02 \\,\xfd^|\x11\xd6\xdd\x8b"
                b" nc\x1aD_go\x8b#\xea\x0c\xcct\xbc\x80.\xb0:\xbb\xec\x80\x92"
            ),
        ),
        (
            True,
            True,
            False,
            False,
            (
                b"0E\x02!\x00\xf0\xe4\x9e\xa1\x1b\x99A\x0e\xcb:;D\x96YIo\x93J\xb5\xaf"
                b"\x80(p\x11\x08\xf4\xdfA\xc8\xe1\xfe\xac\x02 \\,\xfd^|\x11\xd6\xdd\x8b"
                b" nc\x1aD_go\x8b#\xea\x0c\xcct\xbc\x80.\xb0:\xbb\xec\x80\x920E\x02!"
                b"\x00\xff\xf7\n\xdd\x8d\xb1\xd5M\x1cPL5D\x17\xc2\xbaZ\x03@\x1e\x93\xcd"
                b"\x9e\xc3\xf7V\x05\xa6H\x88\xd0E\x02 <p\xc1\xa8l<Aj\xf9\x13\xa4\xd6W"
                b'\xb4a\xd7?"\x97\x06\x18\x01\x98$c\xd7\xbdG\xf5\xa9\x1c\xfe'
            ),
        ),
        (
            True,
            True,
            False,
            False,
            (
                b"0E\x02!\x00\xf0\xe4\x9e\xa1\x1b\x99A\x0e\xcb:;D\x96YIo\x93J\xb5\xaf"
                b"\x80(p\x11\x08\xf4\xdfA\xc8\xe1\xfe\xac\x02 \\,\xfd^|\x11\xd6\xdd\x8b"
                b" nc\x1aD_go\x8b#\xea\x0c\xcct\xbc\x80.\xb0:\xbb\xec\x80\x920E\x02!"
                b"\x00\xff\xf7\n\xdd\x8d\xb1\xd5M\x1cPL5D\x17\xc2\xbaZ\x03@\x1e\x93\xcd"
                b"\x9e\xc3\xf7V\x05\xa6H\x88\xd0E\x02 <p\xc1\xa8l<Aj\xf9\x13\xa4\xd6W"
                b'\xb4a\xd7?"\x97\x06\x18\x01\x98$c\xd7\xbdG\xf5\xa9\x1c\xfe'
            ),
        ),
        (
            True,
            True,
            False,
            False,
            (
                b"0E\x02!\x00\xf0\xe4\x9e\xa1\x1b\x99A\x0e\xcb:;D\x96YIo\x93J\xb5\xaf"
                b"\x80(p\x11\x08\xf4\xdfA\xc8\xe1\xfe\xac\x02 \\,\xfd^|\x11\xd6\xdd\x8b"
                b" nc\x1aD_go\x8b#\xea\x0c\xcct\xbc\x80.\xb0:\xbb\xec\x80\x920E\x02!"
                b"\x00\xff\xf7\n\xdd\x8d\xb1\xd5M\x1cPL5D\x17\xc2\xbaZ\x03@\x1e\x93\xcd"
                b"\x9e\xc3\xf7V\x05\xa6H\x88\xd0E\x02 <p\xc1\xa8l<Aj\xf9\x13\xa4\xd6W"
                b'\xb4a\xd7?"\x97\x06\x18\x01\x98$c\xd7\xbdG\xf5\xa9\x1c\xfe\xff0E\x02!'
                b"\x00\xe1\xdf\xf5\xc0\xa4(\x9f\xfe\xe8\xca\xa7\x9f\xd2_\xe8o\r\xedM"
                b"\xaa\xeb\x9f%\xe1#\xea2{\x01\xfd\xb9q\x02 Gm\xa4\xd1we/\xe4\xa3u\xe4"
                b"\x14\x08\x9c\xe8\xc8h\x00\xbc\xc4\xcal\xe0\xb6\xd9t\xef\x98\xd8\xc9"
                b"\xd4\xcf0E\x02!\x00\xae\xf4\x82\xec\xae\xa6\xec\xaf\x8eo\x86\xbdz"
                b"\xc4tE\x8eev\x14\xb3\xeb\x9eD\x07\x89T\x9d\x1e\xa8_`\x02 \\uv4\x11"
                b'\xe0\xfe\xbb}\x11\xa7\xcc\xf7\xcb\x82o\xc1\x1d\xdb\xe3r+s\xf7~"\xe9'
                b"\xf0\x91\x9e\x17\x9d"
            ),
        ),
        (
            True,
            False,
            True,
            False,
            (
                b"0E\x02!\x00\xf0\xe4\x9e\xa1\x1b\x99A\x0e\xcb:;D\x96YIo\x93J\xb5\xaf"
                b"\x80(p\x11\x08\xf4\xdfA\xc8\xe1\xfe\xac\x02 \\,\xfd^|\x11\xd6\xdd\x8b"
                b" nc\x1aD_go\x8b#\xea\x0c\xcct\xbc\x80.\xb0:\xbb\xec\x80\x920D\x02 Y"
                b"\xab\x88\xd3\xfe\x83\xd6\xb5-\xdd^\x866\x96Aah\xf9\xca\xc6\xde\x96#hX"
                b"z\xd745B\xf9\x9f\x02 z\x95\xcaG0\x06\xabW\xde\xe6\xb0n\x06\xf8\xfa"
                b'\x8f\x1b&\x05H\xb9"f\x14\xa0\xe1\xf7`\xcc\x91\x04y'
            ),
        ),
        (False, False, True, False, b""),
        (False, True, False, False, b""),
        (False, False, True, True, b""),
        (False, True, False, True, b""),
        (
            True,
            False,
            False,
            True,
            (
                b"0E\x02!\x00\xf0\xe4\x9e\xa1\x1b\x99A\x0e\xcb:;D\x96YIo\x93J\xb5\xaf"
                b"\x80(p\x11\x08\xf4\xdfA\xc8\xe1\xfe\xac\x02 \\,\xfd^|\x11\xd6\xdd\x8b"
                b" nc\x1aD_go\x8b#\xea\x0c\xcct\xbc\x80.\xb0:\xbb\xec\x80\x92\xff0E\x02"
                b"!\x00\xe1\xdf\xf5\xc0\xa4(\x9f\xfe\xe8\xca\xa7\x9f\xd2_\xe8o\r\xedM"
                b"\xaa\xeb\x9f%\xe1#\xea2{\x01\xfd\xb9q\x02 Gm\xa4\xd1we/\xe4\xa3u\xe4"
                b"\x14\x08\x9c\xe8\xc8h\x00\xbc\xc4\xcal\xe0\xb6\xd9t\xef\x98\xd8\xc9"
                b"\xd4\xcf0E\x02!\x00\xae\xf4\x82\xec\xae\xa6\xec\xaf\x8eo\x86\xbdz\xc4"
                b"tE\x8eev\x14\xb3\xeb\x9eD\x07\x89T\x9d\x1e\xa8_`\x02 \\uv4\x11\xe0"
                b'\xfe\xbb}\x11\xa7\xcc\xf7\xcb\x82o\xc1\x1d\xdb\xe3r+s\xf7~"\xe9\xf0'
                b"\x91\x9e\x17\x9d"
            ),
        ),
    ],
)
def test_deserialize_signatures(
    signature, second_signature, sign_signature, signatures, bytes_data
):
    transaction = BaseTransaction()
    buff = ByteBuffer(bytes_data)
    transaction._deserialize_signature(buff)

    # Sign signature is always false as sign_signature was renamed to second_signature
    assert transaction.sign_signature is None

    if signature:
        assert transaction.signature == (
            "3045022100f0e49ea11b99410ecb3a3b449659496f934ab5af8028701108f4df41c8e1feac"
            "02205c2cfd5e7c11d6dd8b206e631a445f676f8b23ea0ccc74bc802eb03abbec8092"
        )
        if sign_signature:
            assert transaction.second_signature == (
                "3044022059ab88d3fe83d6b52ddd5e863696416168f9cac6de962368587ad7343542f9"
                "9f02207a95ca473006ab57dee6b06e06f8fa8f1b260548b9226614a0e1f760cc910479"
            )
        elif second_signature:
            assert transaction.second_signature == (
                "3045022100fff70add8db1d54d1c504c354417c2ba5a03401e93cd9ec3f75605a64888"
                "d04502203c70c1a86c3c416af913a4d657b461d73f2297061801982463d7bd47f5a91c"
                "fe"
            )
        else:
            assert transaction.second_signature is None

        if signatures:
            assert transaction.signatures == [
                (
                    "3045022100e1dff5c0a4289ffee8caa79fd25fe86f0ded4daaeb9f25e123ea327b"
                    "01fdb9710220476da4d177652fe4a375e414089ce8c86800bcc4ca6ce0b6d974ef"
                    "98d8c9d4cf"
                ),
                (
                    "3045022100aef482ecaea6ecaf8e6f86bd7ac474458e657614b3eb9e440789549d"
                    "1ea85f6002205c75763411e0febb7d11a7ccf7cb826fc11ddbe3722b73f77e22e9"
                    "f0919e179d"
                ),
            ]
        else:
            assert transaction.signatures == []
    else:
        assert transaction.signature is None
        assert transaction.second_signature is None
        assert transaction.signatures == []


def test_apply_v1_compatibility_only_works_for_version_1():
    transaction = BaseTransaction()
    transaction.version = 0
    transaction.second_signature = (
        "3045022100fff70add8db1d54d1c504c354417c2ba5a03401e93cd9ec3f75605a64888d045"
        "02203c70c1a86c3c416af913a4d657b461d73f2297061801982463d7bd47f5a91cfe"
    )
    transaction._apply_v1_compatibility()
    assert transaction.sign_signature is None


def test_apply_v1_compatibility_sets_sign_signature_as_second_signature():
    transaction = BaseTransaction()
    transaction.version = 1
    transaction.second_signature = (
        "3045022100fff70add8db1d54d1c504c354417c2ba5a03401e93cd9ec3f75605a64888d045"
        "02203c70c1a86c3c416af913a4d657b461d73f2297061801982463d7bd47f5a91cfe"
    )
    transaction._apply_v1_compatibility()
    assert transaction.sign_signature == transaction.second_signature


def test_apply_v1_compatibility_sets_recipient_id_for_vote():
    transaction = BaseTransaction()
    transaction.version = 1
    transaction.type = TRANSACTION_TYPE_VOTE
    transaction.sender_public_key = (
        "034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498"
    )
    transaction._apply_v1_compatibility()
    assert transaction.recipient_id == "AS2YSSDbbXBAehfbm1KAEvJMJFdPPT2aRT"


def test_apply_v1_compatibility_sets_keysgroup():
    transaction = BaseTransaction()
    transaction.version = 1
    transaction.type = TRANSACTION_TYPE_MULTI_SIGNATURE
    transaction.asset["multisignature"] = {
        "keysgroup": [
            "034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498",
            "+03e88b0c85ea85697c3db8fd6ea08bba896339ededff04439f48c54d36e2ff9853",
        ]
    }
    transaction._apply_v1_compatibility()
    assert transaction.asset["multisignature"] == {
        "keysgroup": [
            "+034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498",
            "+03e88b0c85ea85697c3db8fd6ea08bba896339ededff04439f48c54d36e2ff9853",
        ]
    }


# def test_serialize(crypto_transaction, dummy_transaction_hash):
#     serialized = crypto_transaction.serialize()
#     assert serialized == dummy_transaction_hash


def test_deserialize(dummy_transaction_hash):
    transaction = BaseTransaction()
    transaction.deserialize(dummy_transaction_hash)

    assert transaction.version == 1
    assert transaction.network == 23
    assert transaction.type == TRANSACTION_TYPE_TRANSFER
    assert transaction.timestamp == 67048949
    assert transaction.sender_public_key == (
        "034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498"
    )
    assert transaction.fee == 342000
    assert transaction.vendor_field == "Patrick Star"
    assert transaction.amount == 100000000
    assert transaction.expiration == 0
    assert transaction.recipient_id == "AFnw7orqn9B4HBKrKawJgfn5dvoL7zr38B"
    assert transaction.signature == (
        "3045022100f0e49ea11b99410ecb3a3b449659496f934ab5af8028701108f4df41c8e1feac"
        "02205c2cfd5e7c11d6dd8b206e631a445f676f8b23ea0ccc74bc802eb03abbec8092"
    )


def test_deserialize_of_special_characters_works_correctly():
    serialized = (
        b"ff011e00b5de110302d832db873622ebdd50e3e79a851d25172d7c66123015d77700f85a35995"
        b"47f4740420f000000000030e28a81e28a81e28a81e28a81e28a81e28a81e28a81e28a81e28a81"
        b"e28a81e28a81e28a81e28a81e28a81e28a81e28a810100000000000000000000001e30993aaa8"
        b"d686cf1a840c75ed2dec0411c43799e3044022053f1c24d19dddb937c93f9f8c526b06a49ef0d"
        b"c246ab2b04675130bc0ddd07ca02201c91f0ec1e8c53498aaeaa8f11565f4dbb79c12be756c8e"
        b"7f6625104212a217b"
    )
    transaction = BaseTransaction.from_serialized(serialized)
    assert transaction.vendor_field == "⊁⊁⊁⊁⊁⊁⊁⊁⊁⊁⊁⊁⊁⊁⊁⊁"


def test_get_bytes(crypto_transaction):
    crypto_transaction.sign_signature = (
        "3045022100fff70add8db1d54d1c504c354417c2ba5a03401e93cd9ec3f75605a64888d045"
        "02203c70c1a86c3c416af913a4d657b461d73f2297061801982463d7bd47f5a91cfe"
    )
    bytes_data = crypto_transaction.get_bytes()
    assert isinstance(bytes_data, bytes)
    assert len(bytes_data) == 281
    assert bytes_data == (
        b"\x00\xf5\x15\xff\x03\x03J\xff\xde\xe0\xef\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5"
        b"\xb8\n\xdc\xcc\x84$E\xa1\x87\xb2\xf8\x0f+\xb4\\r\xc4\x98\x17\x003P4Bp2\xfb,."
        b"\xee\x9cY\xe7\xf7\xc0\xea\xe0\xc0\xdePatrick Star\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\xe1\xf5\x05\x00\x00\x00\x00\xf07\x05\x00\x00"
        b"\x00\x00\x000E\x02!\x00\xf0\xe4\x9e\xa1\x1b\x99A\x0e\xcb:;D\x96YIo\x93J\xb5"
        b"\xaf\x80(p\x11\x08\xf4\xdfA\xc8\xe1\xfe\xac\x02 \\,\xfd^|\x11\xd6\xdd\x8b nc"
        b"\x1aD_go\x8b#\xea\x0c\xcct\xbc\x80.\xb0:\xbb\xec\x80\x920E\x02!\x00\xff\xf7\n"
        b"\xdd\x8d\xb1\xd5M\x1cPL5D\x17\xc2\xbaZ\x03@\x1e\x93\xcd\x9e\xc3\xf7V\x05\xa6H"
        b'\x88\xd0E\x02 <p\xc1\xa8l<Aj\xf9\x13\xa4\xd6W\xb4a\xd7?"\x97\x06\x18\x01\x98'
        b"$c\xd7\xbdG\xf5\xa9\x1c\xfe"
    )


def test_get_bytes_without_signature(crypto_transaction):
    crypto_transaction.sign_signature = (
        "3045022100fff70add8db1d54d1c504c354417c2ba5a03401e93cd9ec3f75605a64888d045"
        "02203c70c1a86c3c416af913a4d657b461d73f2297061801982463d7bd47f5a91cfe"
    )
    bytes_data = crypto_transaction.get_bytes(skip_signature=True)
    assert isinstance(bytes_data, bytes)
    assert len(bytes_data) == 210
    assert bytes_data == (
        b"\x00\xf5\x15\xff\x03\x03J\xff\xde\xe0\xef\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5"
        b"\xb8\n\xdc\xcc\x84$E\xa1\x87\xb2\xf8\x0f+\xb4\\r\xc4\x98\x17\x003P4Bp2\xfb,."
        b"\xee\x9cY\xe7\xf7\xc0\xea\xe0\xc0\xdePatrick Star\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\xe1\xf5\x05\x00\x00\x00\x00\xf07\x05\x00\x00"
        b"\x00\x00\x000E\x02!\x00\xff\xf7\n\xdd\x8d\xb1\xd5M\x1cPL5D\x17\xc2\xbaZ\x03@"
        b"\x1e\x93\xcd\x9e\xc3\xf7V\x05\xa6H\x88\xd0E\x02 <p\xc1\xa8l<Aj\xf9\x13\xa4"
        b'\xd6W\xb4a\xd7?"\x97\x06\x18\x01\x98$c\xd7\xbdG\xf5\xa9\x1c\xfe'
    )


def test_get_bytes_without_second_signature(crypto_transaction):
    crypto_transaction.sign_signature = (
        "3045022100fff70add8db1d54d1c504c354417c2ba5a03401e93cd9ec3f75605a64888d045"
        "02203c70c1a86c3c416af913a4d657b461d73f2297061801982463d7bd47f5a91cfe"
    )
    bytes_data = crypto_transaction.get_bytes(skip_second_signature=True)
    assert isinstance(bytes_data, bytes)
    assert len(bytes_data) == 210
    assert bytes_data == (
        b"\x00\xf5\x15\xff\x03\x03J\xff\xde\xe0\xef\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5"
        b"\xb8\n\xdc\xcc\x84$E\xa1\x87\xb2\xf8\x0f+\xb4\\r\xc4\x98\x17\x003P4Bp2\xfb,."
        b"\xee\x9cY\xe7\xf7\xc0\xea\xe0\xc0\xdePatrick Star\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\xe1\xf5\x05\x00\x00\x00\x00\xf07\x05\x00\x00"
        b"\x00\x00\x000E\x02!\x00\xf0\xe4\x9e\xa1\x1b\x99A\x0e\xcb:;D\x96YIo\x93J\xb5"
        b"\xaf\x80(p\x11\x08\xf4\xdfA\xc8\xe1\xfe\xac\x02 \\,\xfd^|\x11\xd6\xdd\x8b nc"
        b"\x1aD_go\x8b#\xea\x0c\xcct\xbc\x80.\xb0:\xbb\xec\x80\x92"
    )


def test_get_bytes_raises_for_invalid_version(crypto_transaction):
    crypto_transaction.version = 2
    with pytest.raises(Exception):
        crypto_transaction.get_bytes(True, True)


def test_get_bytes_transaction_second_signature(crypto_transaction):
    crypto_transaction.asset = {
        "signature": {
            "publicKey": (
                "034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498"
            )
        }
    }
    crypto_transaction.recipient_id = None
    crypto_transaction.type = TRANSACTION_TYPE_SECOND_SIGNATURE
    bytes_data = crypto_transaction.get_bytes(True, True)
    assert isinstance(bytes_data, bytes)
    assert len(bytes_data) == 172
    assert bytes_data == (
        b"\x01\xf5\x15\xff\x03\x03J\xff\xde\xe0\xef\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5"
        b"\xb8\n\xdc\xcc\x84$E\xa1\x87\xb2\xf8\x0f+\xb4\\r\xc4\x98\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00Patrick Star"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe1\xf5\x05\x00"
        b"\x00\x00\x00\xf07\x05\x00\x00\x00\x00\x00\x03J\xff\xde\xe0\xef\x07\xd4\xf0"
        b"\x7f\xda\x19\xfc+\xe5\xb8\n\xdc\xcc\x84$E\xa1\x87\xb2\xf8\x0f+\xb4\\r\xc4\x98"
    )


def test_get_bytes_transaction_multisignature(crypto_transaction):
    crypto_transaction.asset = {
        "multisignature": {
            "keysgroup": [
                "034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498",
                "+03e88b0c85ea85697c3db8fd6ea08bba896339ededff04439f48c54d36e2ff9853",
            ],
            "min": 5,
            "lifetime": 3,
        }
    }
    crypto_transaction.recipient_id = None
    crypto_transaction.type = TRANSACTION_TYPE_MULTI_SIGNATURE
    bytes_data = crypto_transaction.get_bytes(True, True)
    assert isinstance(bytes_data, bytes)
    assert len(bytes_data) == 274
    assert bytes_data == (
        b"\x04\xf5\x15\xff\x03\x03J\xff\xde\xe0\xef\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5"
        b"\xb8\n\xdc\xcc\x84$E\xa1\x87\xb2\xf8\x0f+\xb4\\r\xc4\x98\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00Patrick Star"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe1\xf5\x05\x00"
        b"\x00\x00\x00\xf07\x05\x00\x00\x00\x00\x00\x05\x03034affdee0ef07d4f07fda19fc2"
        b"be5b80adccc842445a187b2f80f2bb45c72c498+03e88b0c85ea85697c3db8fd6ea08bba8963"
        b"39ededff04439f48c54d36e2ff9853"
    )


def test_get_bytes_transaction_vote(crypto_transaction):
    crypto_transaction.asset = {
        "votes": ["+034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498"]
    }
    crypto_transaction.type = TRANSACTION_TYPE_VOTE
    bytes_data = crypto_transaction.get_bytes(True, True)
    assert isinstance(bytes_data, bytes)
    assert len(bytes_data) == 206
    assert bytes_data == (
        b"\x03\xf5\x15\xff\x03\x03J\xff\xde\xe0\xef\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5"
        b"\xb8\n\xdc\xcc\x84$E\xa1\x87\xb2\xf8\x0f+\xb4\\r\xc4\x98\x17\x003P4Bp2\xfb,."
        b"\xee\x9cY\xe7\xf7\xc0\xea\xe0\xc0\xdePatrick Star\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\xe1\xf5\x05\x00\x00\x00\x00\xf07\x05\x00\x00"
        b"\x00\x00\x00+034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c4"
        b"98"
    )


def test_get_bytes_transaction_delegate_registration(crypto_transaction):
    crypto_transaction.asset = {"delegate": {"username": "harambe"}}
    crypto_transaction.type = TRANSACTION_TYPE_DELEGATE_REGISTRATION
    bytes_data = crypto_transaction.get_bytes(True, True)
    assert isinstance(bytes_data, bytes)
    assert len(bytes_data) == 146
    assert bytes_data == (
        b"\x02\xf5\x15\xff\x03\x03J\xff\xde\xe0\xef\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5"
        b"\xb8\n\xdc\xcc\x84$E\xa1\x87\xb2\xf8\x0f+\xb4\\r\xc4\x98\x17\x003P4Bp2\xfb,."
        b"\xee\x9cY\xe7\xf7\xc0\xea\xe0\xc0\xdePatrick Star\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\xe1\xf5\x05\x00\x00\x00\x00\xf07\x05\x00\x00"
        b"\x00\x00\x00harambe"
    )


def test_get_bytes_transaction_exception(crypto_transaction, mocker):
    crypto_transaction.recipient_id = None
    mocker.patch(
        "chain.crypto.objects.transactions.base.is_transaction_exception",
        return_value=True,
    )
    bytes_data = crypto_transaction.get_bytes(True, True)
    assert isinstance(bytes_data, bytes)
    assert len(bytes_data) == 139
    assert bytes_data == (
        b"\x00\xf5\x15\xff\x03\x03J\xff\xde\xe0\xef\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5"
        b"\xb8\n\xdc\xcc\x84$E\xa1\x87\xb2\xf8\x0f+\xb4\\r\xc4\x98\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00Patrick Star"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe1\xf5\x05\x00"
        b"\x00\x00\x00\xf07\x05\x00\x00\x00\x00\x00"
    )


def test_get_bytes_vendor_field(crypto_transaction):
    crypto_transaction.vendor_field = "Patrick Star"
    bytes_data = crypto_transaction.get_bytes(True, True)
    assert isinstance(bytes_data, bytes)
    assert len(bytes_data) == 139
    assert bytes_data == (
        b"\x00\xf5\x15\xff\x03\x03J\xff\xde\xe0\xef\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5"
        b"\xb8\n\xdc\xcc\x84$E\xa1\x87\xb2\xf8\x0f+\xb4\\r\xc4\x98\x17\x003P4Bp2\xfb,."
        b"\xee\x9cY\xe7\xf7\xc0\xea\xe0\xc0\xdePatrick Star\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\xe1\xf5\x05\x00\x00\x00\x00\xf07\x05\x00\x00"
        b"\x00\x00\x00"
    )


def test_get_bytes_no_vendor_field(crypto_transaction):
    crypto_transaction.vendor_field = None
    bytes_data = crypto_transaction.get_bytes(True, True)
    assert isinstance(bytes_data, bytes)
    assert len(bytes_data) == 139
    assert bytes_data == (
        b"\x00\xf5\x15\xff\x03\x03J\xff\xde\xe0\xef\x07\xd4\xf0\x7f\xda\x19\xfc+\xe5"
        b"\xb8\n\xdc\xcc\x84$E\xa1\x87\xb2\xf8\x0f+\xb4\\r\xc4\x98\x17\x003P4Bp2\xfb,."
        b"\xee\x9cY\xe7\xf7\xc0\xea\xe0\xc0\xde\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe1\xf5"
        b"\x05\x00\x00\x00\x00\xf07\x05\x00\x00\x00\x00\x00"
    )


def test_verify(crypto_transaction):
    assert crypto_transaction.verify() is True


def test_verify_wrong_version(crypto_transaction):
    crypto_transaction.version = 123
    assert crypto_transaction.verify() is False


def test_verify_no_signature(crypto_transaction):
    crypto_transaction.signature = None
    assert crypto_transaction.verify() is False


def test_get_hash(crypto_transaction):
    transaction_hash = crypto_transaction.get_hash()
    assert (
        transaction_hash
        == "f861b25c9a87fc8913282da8855ee63b9cbaa9324543377a5bdfc5afccb92aaa"
    )


def test_get_id(crypto_transaction):
    transaction_id = crypto_transaction.get_id()
    assert (
        transaction_id
        == "f861b25c9a87fc8913282da8855ee63b9cbaa9324543377a5bdfc5afccb92aaa"
    )


def test_get_id_for_transaction_exception(crypto_transaction, mocker):
    mocker.patch.dict(
        "chain.crypto.objects.transactions.base.config.exceptions",
        {
            "transactionIdFixTable": {
                "f861b25c9a87fc8913282da8855ee63b9cbaa9324543377a5bdfc5afccb92aaa": (
                    "harambe"
                )
            }
        },
        clear=True,
    )

    transaction_id = crypto_transaction.get_id()
    assert transaction_id == "harambe"


def test_to_json(crypto_transaction):
    data = crypto_transaction.to_json()
    assert data == {
        "version": None,
        "network": None,
        "type": 0,
        "timestamp": 67048949,
        "senderPublicKey": (
            "034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498"
        ),
        "fee": "342000",
        "amount": "100000000",
        "expiration": 0,
        "recipientId": "AFnw7orqn9B4HBKrKawJgfn5dvoL7zr38B",
        "asset": {},
        "vendorField": "Patrick Star",
        "id": "f861b25c9a87fc8913282da8855ee63b9cbaa9324543377a5bdfc5afccb92aaa",
        "signature": (
            "3045022100f0e49ea11b99410ecb3a3b449659496f934ab5af8028701108f4df41c8e1feac"
            "02205c2cfd5e7c11d6dd8b206e631a445f676f8b23ea0ccc74bc802eb03abbec8092"
        ),
        "secondSignature": None,
        "signSignature": None,
        "signatures": [],
        "blockId": None,
        "sequence": 0,
        "timelock": None,
        "timelockType": None,
        "ipfsHash": None,
        "payments": None,
    }


def test_calculate_expires_at_with_expiration_set(crypto_transaction):
    crypto_transaction.expiration = 5
    expires_at = crypto_transaction.calculate_expires_at(1337)
    assert expires_at == 5


def test_calculate_expires_at_without_expiration_set(crypto_transaction):
    crypto_transaction.expiration = None
    expires_at = crypto_transaction.calculate_expires_at(1337)
    assert expires_at == 67050286


def test_calculate_expires_at_for_timelock_transfer(crypto_transaction):
    crypto_transaction.type = TRANSACTION_TYPE_TIMELOCK_TRANSFER
    expires_at = crypto_transaction.calculate_expires_at(1337)
    assert expires_at is None


def test_can_be_applied_to_wallet_returns_false_if_wallet_has_multisignature():
    transaction = BaseTransaction()
    wallet = Wallet({"multisignature": "harambe"})
    can_apply = transaction.can_be_applied_to_wallet(wallet, None, None)
    assert can_apply is False


def test_can_be_applied_to_wallet_returns_false_for_negative_balance():
    transaction = BaseTransaction()
    transaction.amount = 14
    transaction.fee = 2
    wallet = Wallet({"balance": 15})
    can_apply = transaction.can_be_applied_to_wallet(wallet, None, None)
    assert can_apply is False


def test_can_be_applied_to_wallet_returns_false_for_different_public_keys():
    transaction = BaseTransaction()
    transaction.sender_public_key = "abrakadabra"
    wallet = Wallet({"public_key": "harambe"})
    can_apply = transaction.can_be_applied_to_wallet(wallet, None, None)
    assert can_apply is False


def test_can_be_applied_to_wallet():
    transaction = BaseTransaction()
    wallet = Wallet({})
    can_apply = transaction.can_be_applied_to_wallet(wallet, None, None)
    assert can_apply is True


def test_appply_to_sender_wallet(crypto_transaction):
    wallet = Wallet(
        {
            "address": "AS2YSSDbbXBAehfbm1KAEvJMJFdPPT2aRT",
            "public_key": (
                "034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498"
            ),
            "balance": 1000000000,
        }
    )
    crypto_transaction.apply_to_sender_wallet(wallet)

    assert wallet.balance == 899658000


def test_appply_to_sender_wallet_raises_for_wrong_wallet(crypto_transaction):
    wallet = Wallet({"address": "asdf", "public_key": "asdf", "balance": 1000000000})
    with pytest.raises(Exception):
        crypto_transaction.apply_to_sender_wallet(wallet)

    assert wallet.balance == 1000000000


def test_apply_to_recipient_wallet(crypto_transaction):
    wallet = Wallet({"address": "AFnw7orqn9B4HBKrKawJgfn5dvoL7zr38B", "balance": 0})
    crypto_transaction.apply_to_recipient_wallet(wallet)
    assert wallet.balance == 100000000


def test_apply_to_recipient_wallet_raises_for_wrong_address(crypto_transaction):
    wallet = Wallet({"address": "asdfasf", "balance": 0})
    with pytest.raises(Exception):
        crypto_transaction.apply_to_recipient_wallet(wallet)
    assert wallet.balance == 0


def test_revert_for_sender_wallet(crypto_transaction):
    wallet = Wallet(
        {
            "address": "AS2YSSDbbXBAehfbm1KAEvJMJFdPPT2aRT",
            "public_key": (
                "034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498"
            ),
            "balance": 899658000,
        }
    )
    crypto_transaction.revert_for_sender_wallet(wallet)
    assert wallet.balance == 1000000000


def test_revert_for_sender_wallet_raises_for_wrong_address(crypto_transaction):
    wallet = Wallet({"address": "asdf", "public_key": "asdf", "balance": 899658000})
    with pytest.raises(Exception):
        crypto_transaction.revert_for_sender_wallet(wallet)
    assert wallet.balance == 899658000


def test_revert_for_recipient_wallet(crypto_transaction):
    wallet = Wallet(
        {"address": "AFnw7orqn9B4HBKrKawJgfn5dvoL7zr38B", "balance": 100000000}
    )
    crypto_transaction.revert_for_recipient_wallet(wallet)
    assert wallet.balance == 0


def test_revert_for_recipient_wallet_raises_for_wrong_address(crypto_transaction):
    wallet = Wallet({"address": "asdf", "balance": 100000000})
    with pytest.raises(Exception):
        crypto_transaction.revert_for_recipient_wallet(wallet)
    assert wallet.balance == 100000000


def test_validate_for_transaction_pool(crypto_transaction):
    error = crypto_transaction.validate_for_transaction_pool(None, None)
    assert error == "Transaction with type 0 is not supported"
