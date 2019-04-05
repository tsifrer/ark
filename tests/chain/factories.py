import random
import os
from hashlib import sha256

from factory import Factory, LazyAttribute, Sequence

from chain.crypto.constants import TRANSACTION_TYPE_TRANSFER
from chain.plugins.database.models.block import Block
from chain.plugins.database.models.round import Round
from chain.plugins.database.models.transaction import Transaction


class PeeWeeModelFactory(Factory):
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return model_class.create(*args, **kwargs)


class BlockFactory(PeeWeeModelFactory):
    # id = "7176646138626297930"
    id = LazyAttribute(lambda _: ''.join([str(random.randint(0, 9)) for num in range(19)]))
    version = 0
    timestamp = Sequence(lambda n: 24760440 + n * 8)
    height = Sequence(lambda n: 2243161 + n)
    number_of_transactions = 7
    total_amount = 3890300
    total_fee = 70000000
    reward = 200000000
    payload_length = 224
    payload_hash = "3784b953afcf936bdffd43fdf005b5732b49c1fc6b11e195c364c20b2eb06282"
    generator_public_key = (
        "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
    )
    block_signature = (
        "3045022100eee6c37b5e592e99811d588532726353592923f347c701d52912e6d583443e40022"
        "0277ffe38ad31e216ba0907c4738fed19b2071246b150c72c0a52bae4477ebe29"
    )

    class Meta:
        model = Block


class TransactionFactory(PeeWeeModelFactory):
    
    id = LazyAttribute(lambda _: sha256(os.urandom(32)).hexdigest())
    version = 1
    sequence = 0
    timestamp = 51174114
    sender_public_key = (
        "0377450c35e9925d933e4825ef3544f680d39db18264959b08eb9927e0a7c9eaf4"
    )
    type = TRANSACTION_TYPE_TRANSFER
    amount = 1337
    fee = 1000
    serialized = b""

    # 'id': 'a379c51bd27e6f35be1d297f12e90f94c0eb56fc7588cd15f480969513afd125',
    # 'version': 1,
    # 'block_id': '6942490254020282224',
    # 'sequence': 87,
    # 'timestamp': 51174114,
    # 'sender_public_key': '0377450c35e9925d933e4825ef3544f680d39db18264959b08eb9927e0a7c9eaf4',
    # 'recipient_id': 'D9a4Y1qokJxTDEJcfzqW2io1bykdaoW5mp',
    # 'type': 0,
    # 'vendor_field_hex': b'4861707079205370616d6d696e6720233939392f34303030',
    # 'amount': 1,
    # 'fee': 1000,
    # # 'serialized': b'ff011e00e2da0c030377450c35e9925d933e4825ef3544f680d39db18264959b08eb9927e0a7c9eaf4e803000000000000184861707079205370616d6d696e6720233939392f343030300100000000000000000000001e30993aaa8d686cf1a840c75ed2dec0411c43799e304402200a51af93d83a669992cd7836a847d9cec127bc6c94b5cb0ae53d31cff3c66ba4022070e12f6e911ade366c4b7b0b6d9660cae4ccea20620cd6a8002e28cbd1344059'

    class Meta:
        model = Transaction


class RoundFactory(PeeWeeModelFactory):
    class Meta:
        model = Round
