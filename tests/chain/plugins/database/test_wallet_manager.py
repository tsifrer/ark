import json

import pytest

from chain.crypto.constants import (
    TRANSACTION_TYPE_DELEGATE_REGISTRATION,
    TRANSACTION_TYPE_MULTI_SIGNATURE,
    TRANSACTION_TYPE_SECOND_SIGNATURE,
    TRANSACTION_TYPE_TRANSFER,
    TRANSACTION_TYPE_VOTE,
)
from chain.plugins.database.wallet_manager import WalletManager

from tests.chain.factories import BlockFactory, TransactionFactory


def test_find_by_address_correctly_fetches_the_wallet(redis):
    address = "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof"
    key = "wallets:address:{}".format(address).encode()

    manager = WalletManager()
    wallet = manager.find_by_address(address)

    keys = redis.keys("*")
    assert keys == []

    wallet.balance = 12345
    wallet.save()
    keys = redis.keys("*")
    assert keys == [key]

    wallet = manager.find_by_address(address)
    assert wallet.balance == 12345
    keys = redis.keys("*")
    assert keys == [key]


def test_find_by_address_raises_value_error_if_address_is_not_str(redis):
    address = b"AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof"

    manager = WalletManager()
    with pytest.raises(ValueError):
        manager.find_by_address(address)


def test_find_by_public_key_correctly_fetches_the_wallet(redis):
    key = b"wallets:address:AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof"
    public_key = "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
    manager = WalletManager()
    wallet = manager.find_by_public_key(public_key)

    keys = redis.keys("*")
    assert keys == [key]
    assert wallet.public_key == public_key

    wallet.balance = 12345
    wallet.save()
    keys = redis.keys("*")
    assert keys == [key]

    wallet = manager.find_by_public_key(public_key)
    assert wallet.balance == 12345
    keys = redis.keys("*")
    assert keys == [key]


def test_build_received_transactions(empty_db, redis):
    block = BlockFactory()

    TransactionFactory(
        block_id=block.id,
        recipient_id="DB4gFuDztmdGALMb8i1U4Z4R5SktxpNTAY",
        type=TRANSACTION_TYPE_TRANSFER,
        amount=5000,
    )
    TransactionFactory(
        block_id=block.id,
        recipient_id="DB4gFuDztmdGALMb8i1U4Z4R5SktxpNTAY",
        type=TRANSACTION_TYPE_TRANSFER,
        amount=2000,
    )

    TransactionFactory(
        block_id=block.id,
        recipient_id="DGExsNogZR7JFa2656ZFP9TMWJYJh5djzQ",
        type=TRANSACTION_TYPE_TRANSFER,
        amount=13000,
    )

    TransactionFactory(
        block_id=block.id,
        recipient_id="DGExsNogZR7JFa2656ZFP9TMWJYJh5djzQ",
        type=TRANSACTION_TYPE_DELEGATE_REGISTRATION,
        amount=13000,
    )

    manager = WalletManager()
    manager._build_received_transactions()

    keys = redis.keys("*")

    key_1 = b"wallets:address:DB4gFuDztmdGALMb8i1U4Z4R5SktxpNTAY"
    key_2 = b"wallets:address:DGExsNogZR7JFa2656ZFP9TMWJYJh5djzQ"
    assert sorted(keys) == sorted([key_1, key_2])

    wallet_1 = json.loads(redis.get(key_1))
    assert wallet_1 == {
        "address": "DB4gFuDztmdGALMb8i1U4Z4R5SktxpNTAY",
        "public_key": None,
        "second_public_key": None,
        "multisignature": None,
        "vote": None,
        "username": None,
        "balance": 7000,
        "vote_balance": 0,
        "produced_blocks": 0,
        "missed_blocks": 0,
        "forged_fees": 0,
        "forged_rewards": 0,
    }

    wallet_2 = json.loads(redis.get(key_2))
    assert wallet_2 == {
        "address": "DGExsNogZR7JFa2656ZFP9TMWJYJh5djzQ",
        "public_key": None,
        "second_public_key": None,
        "multisignature": None,
        "vote": None,
        "username": None,
        "balance": 13000,
        "vote_balance": 0,
        "produced_blocks": 0,
        "missed_blocks": 0,
        "forged_fees": 0,
        "forged_rewards": 0,
    }


def test_build_block_rewards(empty_db, redis):
    BlockFactory(
        reward=2000,
        total_fee=1000,
        generator_public_key=(
            "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
        ),
    )

    BlockFactory(
        reward=50000,
        total_fee=3000,
        generator_public_key=(
            "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
        ),
    )

    BlockFactory(
        reward=14000,
        total_fee=19000,
        generator_public_key=(
            "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
        ),
    )

    manager = WalletManager()
    manager._build_block_rewards()

    keys = redis.keys("*")
    key_1 = b"wallets:address:AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof"
    key_2 = b"wallets:address:AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW"
    assert sorted(keys) == sorted([key_1, key_2])

    wallet_1 = json.loads(redis.get(key_1))
    assert wallet_1 == {
        "address": "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof",
        "public_key": (
            "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
        ),
        "second_public_key": None,
        "multisignature": None,
        "vote": None,
        "username": None,
        "balance": 56000,
        "vote_balance": 0,
        "produced_blocks": 0,
        "missed_blocks": 0,
        "forged_fees": 0,
        "forged_rewards": 0,
    }

    wallet_2 = json.loads(redis.get(key_2))
    assert wallet_2 == {
        "address": "AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW",
        "public_key": (
            "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
        ),
        "second_public_key": None,
        "multisignature": None,
        "vote": None,
        "username": None,
        "balance": 33000,
        "vote_balance": 0,
        "produced_blocks": 0,
        "missed_blocks": 0,
        "forged_fees": 0,
        "forged_rewards": 0,
    }


def test_build_sent_transactions(empty_db, redis):
    block = BlockFactory()

    TransactionFactory(
        block_id=block.id,
        type=TRANSACTION_TYPE_TRANSFER,
        amount=5000,
        fee=1000,
        sender_public_key="03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
    )
    TransactionFactory(
        block_id=block.id,
        type=TRANSACTION_TYPE_TRANSFER,
        amount=2000,
        fee=4500,
        sender_public_key="020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
    )
    TransactionFactory(
        block_id=block.id,
        type=TRANSACTION_TYPE_TRANSFER,
        amount=13000,
        fee=1300,
        sender_public_key="03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
    )
    TransactionFactory(
        block_id=block.id,
        type=TRANSACTION_TYPE_DELEGATE_REGISTRATION,
        amount=13000,
        fee=3000,
        sender_public_key="020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
    )

    manager = WalletManager()
    manager._build_sent_transactions()

    keys = redis.keys("*")

    key_1 = b"wallets:address:AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof"
    key_2 = b"wallets:address:AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW"
    assert sorted(keys) == sorted([key_1, key_2])

    # TODO: They need to have a negative wallet balance as they've spent this money
    # and in the build code we substract this from their total balance.
    wallet_1 = json.loads(redis.get(key_1))
    assert wallet_1 == {
        "address": "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof",
        "public_key": (
            "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
        ),
        "second_public_key": None,
        "multisignature": None,
        "vote": None,
        "username": None,
        "balance": -22500,
        "vote_balance": 0,
        "produced_blocks": 0,
        "missed_blocks": 0,
        "forged_fees": 0,
        "forged_rewards": 0,
    }

    wallet_2 = json.loads(redis.get(key_2))
    assert wallet_2 == {
        "address": "AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW",
        "public_key": (
            "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
        ),
        "second_public_key": None,
        "multisignature": None,
        "vote": None,
        "username": None,
        "balance": -20300,
        "vote_balance": 0,
        "produced_blocks": 0,
        "missed_blocks": 0,
        "forged_fees": 0,
        "forged_rewards": 0,
    }
