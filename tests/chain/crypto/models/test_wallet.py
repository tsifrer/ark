from chain.crypto.models.wallet import Wallet

# TODO: MOARD TESTS!!!


def test_wallet_sets_default_attributes_with_default_values():
    wallet = Wallet({})
    assert wallet.address is None
    assert wallet.public_key is None
    assert wallet.second_public_key is None
    assert wallet.multisignature is None
    assert wallet.vote is None
    assert wallet.username is None
    assert wallet.balance == 0
    assert wallet.vote_balance == 0
    assert wallet.produced_blocks == 0
    assert wallet.missed_blocks == 0
    assert wallet.forged_fees == 0
    assert wallet.forged_rewards == 0


def test_wallet_sets_attributes_with_correct_values():
    data = {
        "address": "DSMxEhoudwLYVt1jtHDu1dtisa2gS7LeCW",
        "public_key": (
            "023918d30ff448ec897e12b77ccd529835c78aee07db1682639320c253cc21a1c7"
        ),
        "second_public_key": None,
        "multisignature": None,
        "vote": "023918d30ff448ec897e12b77ccd529835c78aee07db1682639320c253cc21a1c7",
        "username": "genesis_6",
        "balance": 600000000,
        "vote_balance": 600000000,
        "produced_blocks": 1,
        "missed_blocks": 0,
        "forged_fees": 0,
        "forged_rewards": 0,
    }
    wallet = Wallet(data)
    assert wallet.address == data["address"]
    assert wallet.public_key == data["public_key"]
    assert wallet.second_public_key == data["second_public_key"]
    assert wallet.multisignature == data["multisignature"]
    assert wallet.vote == data["vote"]
    assert wallet.username == data["username"]
    assert wallet.balance == data["balance"]
    assert wallet.vote_balance == data["vote_balance"]
    assert wallet.produced_blocks == data["produced_blocks"]
    assert wallet.missed_blocks == data["missed_blocks"]
    assert wallet.forged_fees == data["forged_fees"]
    assert wallet.forged_rewards == data["forged_rewards"]
