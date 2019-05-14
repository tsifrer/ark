import pytest

from chain.crypto.constants import TRANSACTION_TYPE_TRANSFER
from chain.crypto.objects.block import Block
from chain.crypto.objects.transactions import BaseTransaction


@pytest.fixture
def dummy_block_full_hash():
    return (
        "0000000078d07901593a22002b324b8b33a85802020000007c5c3b0000000000801d2c04000000"
        "0000c2eb0b00000000e00000003784b953afcf936bdffd43fdf005b5732b49c1fc6b11e195c364"
        "c20b2eb06282020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
        "3045022100eee6c37b5e592e99811d588532726353592923f347c701d52912e6d583443e400220"
        "277ffe38ad31e216ba0907c4738fed19b2071246b150c72c0a52bae4477ebe29a6000000ae0000"
        "00ff011700f515ff03034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c"
        "72c498f0370500000000000c5061747269636b205374617200e1f5050000000000000000170033"
        "5034427032fb2c2eee9c59e7f7c0eae0c0de3045022100f0e49ea11b99410ecb3a3b449659496f"
        "934ab5af8028701108f4df41c8e1feac02205c2cfd5e7c11d6dd8b206e631a445f676f8b23ea0c"
        "cc74bc802eb03abbec8092ff0117002b16ff0303e88b0c85ea85697c3db8fd6ea08bba896339ed"
        "edff04439f48c54d36e2ff9853a0860100000000001553706f6e6765626f622053717561726570"
        "616e747320145d0000000000000000001770777697adc76d51577c83bf2f3dfcb67acbe3063044"
        "022005e701c02340a0e929b223b6a545e6dcb1b0f2faf6eaaed51291cd5fa69fd14302206093f9"
        "d358579f44c304b1e854e7282ba48be79272c8f895dfc555e1937684c4"
    ).encode("utf-8")


@pytest.fixture
def dummy_block_hash():
    return (
        "0000000078d07901593a22002b324b8b33a85802020000007c5c3b0000000000801d2c04000000"
        "0000c2eb0b00000000e00000003784b953afcf936bdffd43fdf005b5732b49c1fc6b11e195c364"
        "c20b2eb06282020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
        "3045022100eee6c37b5e592e99811d588532726353592923f347c701d52912e6d583443e400220"
        "277ffe38ad31e216ba0907c4738fed19b2071246b150c72c0a52bae4477ebe29"
    ).encode("utf-8")


@pytest.fixture
def dummy_transaction_hash():
    return (
        "ff011700f515ff03034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72"
        "c498f0370500000000000c5061747269636b205374617200e1f505000000000000000017003350"
        "34427032fb2c2eee9c59e7f7c0eae0c0de3045022100f0e49ea11b99410ecb3a3b449659496f93"
        "4ab5af8028701108f4df41c8e1feac02205c2cfd5e7c11d6dd8b206e631a445f676f8b23ea0ccc"
        "74bc802eb03abbec8092"
    ).encode("utf-8")


@pytest.fixture
def dummy_transaction():
    return {
        "type": 0,
        "amount": 100000000,
        "fee": 342000,
        "recipientId": "AFnw7orqn9B4HBKrKawJgfn5dvoL7zr38B",
        "timestamp": 67048949,
        "asset": {},
        "vendorField": "Patrick Star",
        "senderPublicKey": (
            "034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498"
        ),
        "signature": (
            "3045022100f0e49ea11b99410ecb3a3b449659496f934ab5af8028701108f4df41c8e1feac"
            "02205c2cfd5e7c11d6dd8b206e631a445f676f8b23ea0ccc74bc802eb03abbec8092"
        ),
        "id": "f861b25c9a87fc8913282da8855ee63b9cbaa9324543377a5bdfc5afccb92aaa",
        "senderId": "AS2YSSDbbXBAehfbm1KAEvJMJFdPPT2aRT",
        "broadcast": False,
    }


@pytest.fixture
def dummy_transaction_2():
    return {
        "type": 0,
        "amount": 6100000,
        "fee": 100000,
        "recipientId": "AS2YSSDbbXBAehfbm1KAEvJMJFdPPT2aRT",
        "timestamp": 67049003,
        "asset": {},
        "vendorField": "Spongebob Squarepants",
        "senderPublicKey": (
            "03e88b0c85ea85697c3db8fd6ea08bba896339ededff04439f48c54d36e2ff9853"
        ),
        "signature": (
            "3044022005e701c02340a0e929b223b6a545e6dcb1b0f2faf6eaaed51291cd5fa69fd14302"
            "206093f9d358579f44c304b1e854e7282ba48be79272c8f895dfc555e1937684c4"
        ),
        "id": "c326a19ededdd77eba08b560488c243c2568b728f3a752e137b68713685510c7",
        "senderId": "AFnw7orqn9B4HBKrKawJgfn5dvoL7zr38B",
        "broadcast": False,
    }


@pytest.fixture
def dummy_block(dummy_transaction, dummy_transaction_2):
    dummy_transaction["block_id"] = "10977713934532967004"
    dummy_transaction_2["block_id"] = "10977713934532967004"
    return {
        "id": "10977713934532967004",
        "version": 0,
        "height": 2243161,
        "timestamp": 24760440,
        "previousBlock": "3112633353705641986",
        "numberOfTransactions": 2,
        "totalAmount": "3890300",
        "totalFee": "70000000",
        "reward": "200000000",
        "payloadLength": 224,
        "payloadHash": (
            "3784b953afcf936bdffd43fdf005b5732b49c1fc6b11e195c364c20b2eb06282"
        ),
        "generatorPublicKey": (
            "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
        ),
        "blockSignature": (
            "3045022100eee6c37b5e592e99811d588532726353592923f347c701d52912e6d583443e40"
            "0220277ffe38ad31e216ba0907c4738fed19b2071246b150c72c0a52bae4477ebe29"
        ),
        "transactions": [dummy_transaction, dummy_transaction_2],
    }


@pytest.fixture
def crypto_transaction():
    transaction = BaseTransaction()
    transaction.type = TRANSACTION_TYPE_TRANSFER
    transaction.timestamp = 67048949
    transaction.sender_public_key = (
        "034affdee0ef07d4f07fda19fc2be5b80adccc842445a187b2f80f2bb45c72c498"
        # Address: AS2YSSDbbXBAehfbm1KAEvJMJFdPPT2aRT
    )
    transaction.fee = 342000
    transaction.amount = 100000000
    transaction.expiration = 0
    transaction.recipient_id = "AFnw7orqn9B4HBKrKawJgfn5dvoL7zr38B"
    transaction.vendor_field = "Patrick Star"
    transaction.id = "f861b25c9a87fc8913282da8855ee63b9cbaa9324543377a5bdfc5afccb92aaa"
    transaction.signature = (
        "3045022100f0e49ea11b99410ecb3a3b449659496f934ab5af8028701108f4df41c8e1feac0220"
        "5c2cfd5e7c11d6dd8b206e631a445f676f8b23ea0ccc74bc802eb03abbec8092"
    )
    transaction.sequence = 0
    return transaction


@pytest.fixture
def crypto_transaction_2():
    transaction = BaseTransaction()
    transaction.type = TRANSACTION_TYPE_TRANSFER
    transaction.timestamp = 67049003
    transaction.sender_public_key = (
        "03e88b0c85ea85697c3db8fd6ea08bba896339ededff04439f48c54d36e2ff9853"
        # Address: AFnw7orqn9B4HBKrKawJgfn5dvoL7zr38B
    )
    transaction.fee = 100000
    transaction.amount = 6100000
    transaction.recipient_id = "AS2YSSDbbXBAehfbm1KAEvJMJFdPPT2aRT"
    transaction.vendor_field = "Spongebob Squarepants"
    transaction.id = "c326a19ededdd77eba08b560488c243c2568b728f3a752e137b68713685510c7"
    transaction.signature = (
        "3044022005e701c02340a0e929b223b6a545e6dcb1b0f2faf6eaaed51291cd5fa69fd143022060"
        "93f9d358579f44c304b1e854e7282ba48be79272c8f895dfc555e1937684c4"
    )
    return transaction


@pytest.fixture
def crypto_block(crypto_transaction, crypto_transaction_2):
    # TODO: Block is not from testnet and it has wrong data and signature
    # Change it once we're able to forge blocks with our code
    block = Block()
    block.height = 2243161
    block.id = "10977713934532967004"
    block.id_hex = b"9858aca939b17a5c"
    block.number_of_transactions = 2
    block.payload_hash = (
        "3784b953afcf936bdffd43fdf005b5732b49c1fc6b11e195c364c20b2eb06282"
    )
    block.payload_length = 224
    block.previous_block = "3112633353705641986"
    block.previous_block_hex = b"2b324b8b33a85802"
    block.reward = 200000000
    block.timestamp = 24760440
    block.total_amount = 3890300
    block.total_fee = 70000000
    block.version = 0
    block.generator_public_key = (
        "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
    )
    block.block_signature = (
        "3045022100eee6c37b5e592e99811d588532726353592923f347c701d52912e6d583443e40022"
        "0277ffe38ad31e216ba0907c4738fed19b2071246b150c72c0a52bae4477ebe29"
    )

    crypto_transaction.block_id = "7176646138626297930"
    crypto_transaction_2.block_id = "7176646138626297930"

    block.transactions = [crypto_transaction, crypto_transaction_2]
    return block
