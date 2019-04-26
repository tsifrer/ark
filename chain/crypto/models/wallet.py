import json

from chain.crypto.address import address_from_public_key


# NOTE: This acts like a model, and it's data is stored in redis


class Wallet(object):
    # TODO: make this mapping better
    # field name, default
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

    def can_be_purged(self):
        return (
            self.balance == 0
            and not self.second_public_key
            and not self.multisignature
            and not self.username
        )
