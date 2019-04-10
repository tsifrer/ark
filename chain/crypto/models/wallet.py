import json
from binascii import unhexlify

from chain.common.config import config
from chain.crypto.address import address_from_public_key
from chain.crypto.constants import (
    TRANSACTION_TYPE_DELEGATE_REGISTRATION,
    TRANSACTION_TYPE_DELEGATE_RESIGNATION,
    TRANSACTION_TYPE_MULTI_PAYMENT,
    TRANSACTION_TYPE_MULTI_SIGNATURE,
    TRANSACTION_TYPE_SECOND_SIGNATURE,
    TRANSACTION_TYPE_VOTE,
)
from chain.crypto.utils import verify_hash


# NOTE: This acts like a model, and it's data is stored in redis


class Wallet(object):
    # TODO: make this mapping better
    # field name, default
    _redis = None
    _key = "wallets:address:{}"
    _username_key = "wallets:username:{}"

    fields = [
        ("address", None),
        ("public_key", None),
        ("second_public_key", None),
        ("multisignature", None),
        ("vote", None),
        ("username", None),
        ("balance", 0),
        ("vote_balance", 0),
        ("produced_blocks", 0),
        ("missed_blocks", 0),
        ("forged_fees", 0),
        ("forged_rewards", 0),
    ]

    def __init__(self, data):
        super().__init__()
        for field, default in self.fields:
            setattr(self, field, data.get(field, default))

    @classmethod
    def get(cls, address):
        key = cls._key.format(address)
        data = cls._redis.get(key)
        if data is None:
            return None
        return cls(json.loads(data))

    @property
    def key(self):
        return self._key.format(self.address)

    @property
    def username_key(self):
        return self._username_key.format(self.username.lower())

    def save(self):
        self._redis.set(self.key, self.to_json())

    def to_json(self):
        data = {}
        for field, _ in self.fields:
            data[field] = getattr(self, field)
        return json.dumps(data)

    def apply_block(self, block):
        address = address_from_public_key(block.generator_public_key)
        is_correct_wallet = (
            block.generator_public_key == self.public_key or address == self.address
        )
        if is_correct_wallet:
            self.balance += block.reward
            self.balance += block.total_fee

            self.produced_blocks += 1
            self.forged_fees += block.total_fee
            self.forged_rewards += block.reward
        else:
            raise Exception(
                "Couldn't apply block {} to wallet {}".format(block.id, self.public_key)
            )

    def revert_block(self, block):
        address = address_from_public_key(block.generator_public_key)
        if block.generator_public_key == self.public_key and address == self.address:
            self.balance -= block.reward + block.total_fee

            self.forged_fees -= block.total_fee
            self.forged_rewards -= block.reward
        else:
            raise Exception(
                "Couldn't revert block {} for wallet {}".format(
                    block.id, self.public_key
                )
            )
