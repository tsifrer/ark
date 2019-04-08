import os
import random
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
    id = LazyAttribute(
        lambda _: "".join([str(random.randint(0, 9)) for num in range(19)])
    )
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

    class Meta:
        model = Transaction


class RoundFactory(PeeWeeModelFactory):
    class Meta:
        model = Round
