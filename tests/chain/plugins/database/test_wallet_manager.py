import json

import pytest

from chain.crypto.constants import (
    TRANSACTION_TYPE_DELEGATE_REGISTRATION,
    TRANSACTION_TYPE_MULTI_SIGNATURE,
    TRANSACTION_TYPE_SECOND_SIGNATURE,
    TRANSACTION_TYPE_TRANSFER,
    TRANSACTION_TYPE_VOTE,
)
from chain.crypto.models.wallet import Wallet
from chain.crypto.objects.transactions import TransferTransaction, VoteTransaction
from chain.plugins.database.wallet_manager import WalletManager

from tests.chain.factories import BlockFactory, TransactionFactory


def test_key_for_address():
    manager = WalletManager()
    key = manager.key_for_address("spongebob")
    assert key == "wallets:address:spongebob"


def test_key_for_username():
    manager = WalletManager()
    key = manager.key_for_username("spongebob")
    assert key == "wallets:username:spongebob"


def test_save_wallet_saves_wallet_to_redis(redis):
    manager = WalletManager()
    wallet = Wallet({"address": "spongebob", "username": "squarepants"})
    manager.save_wallet(wallet)

    keys = redis.keys("*")
    assert keys == [b"wallets:address:spongebob"]


def test_find_by_address_returns_a_new_wallet_if_does_not_exist(redis):
    address = "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof"

    manager = WalletManager()
    wallet = manager.find_by_address(address)

    assert wallet.address == address
    assert wallet.public_key is None

    keys = redis.keys("*")
    assert keys == []


def test_find_by_address_returns_existing_wallet(redis):
    address = "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof"
    key = "wallets:address:{}".format(address).encode()
    manager = WalletManager()

    redis.set(key, Wallet({"address": address, "username": "spongebob"}).to_json())

    wallet = manager.find_by_address(address)

    assert wallet.address == address
    assert wallet.username == "spongebob"

    keys = redis.keys("*")
    assert keys == [key]


def test_find_by_address_raises_value_error_if_address_is_not_str(redis):
    address = b"AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof"

    manager = WalletManager()
    with pytest.raises(ValueError):
        manager.find_by_address(address)


def test_find_by_public_key_returns_a_new_wallet_if_does_not_exist(redis):
    address = "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof"
    key = "wallets:address:{}".format(address).encode()
    public_key = "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"

    manager = WalletManager()
    wallet = manager.find_by_public_key(public_key)

    assert wallet.address == address
    assert wallet.public_key == public_key

    # find_by_public_key saves the wallet as it adds public_key to it
    keys = redis.keys("*")
    assert keys == [key]


def test_find_by_public_key_returns_existing_wallet(redis):
    address = "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof"
    public_key = "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
    key = "wallets:address:{}".format(address).encode()
    manager = WalletManager()

    redis.set(key, Wallet({"address": address, "public_key": public_key}).to_json())

    wallet = manager.find_by_public_key(public_key)

    assert wallet.address == address
    assert wallet.public_key == public_key

    keys = redis.keys("*")
    assert keys == [key]


def test_get_wallet_by_address_returns_non_if_wallet_not_in_redis():
    manager = WalletManager()
    wallet = manager._get_wallet_by_address("spongebob")
    assert wallet is None


def test_get_wallet_by_address_returns_correct_wallet(redis):
    manager = WalletManager()

    redis.set(
        "wallets:address:spongebob",
        Wallet({"address": "spongebob", "username": "squarepants"}).to_json(),
    )
    redis.set(
        "wallets:address:patrick",
        Wallet({"address": "patrick", "username": "star"}).to_json(),
    )

    wallet = manager._get_wallet_by_address("spongebob")
    assert wallet.address == "spongebob"
    assert wallet.username == "squarepants"


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
        sender_public_key=(
            "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
        ),
    )
    TransactionFactory(
        block_id=block.id,
        type=TRANSACTION_TYPE_TRANSFER,
        amount=2000,
        fee=4500,
        sender_public_key=(
            "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
        ),
    )
    TransactionFactory(
        block_id=block.id,
        type=TRANSACTION_TYPE_TRANSFER,
        amount=13000,
        fee=1300,
        sender_public_key=(
            "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
        ),
    )
    TransactionFactory(
        block_id=block.id,
        type=TRANSACTION_TYPE_DELEGATE_REGISTRATION,
        amount=13000,
        fee=3000,
        sender_public_key=(
            "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
        ),
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


def test_build_second_signatures(empty_db, redis):
    block = BlockFactory()

    TransactionFactory(
        block_id=block.id,
        type=TRANSACTION_TYPE_SECOND_SIGNATURE,
        asset={
            "signature": {
                "publicKey": (
                    "120f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a334"
                )
            }
        },
        sender_public_key=(
            "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
        ),
    )
    TransactionFactory(
        block_id=block.id,
        type=TRANSACTION_TYPE_TRANSFER,
        amount=13000,
        fee=3000,
        sender_public_key=(
            "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
        ),
    )

    manager = WalletManager()
    manager._build_second_signatures()

    data = json.loads(redis.get("wallets:address:AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW"))

    assert data["address"] == "AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW"
    assert (
        data["public_key"]
        == "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
    )
    assert (
        data["second_public_key"]
        == "120f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a334"
    )


def test_build_votes(empty_db, redis):
    manager = WalletManager()
    block = BlockFactory()

    TransactionFactory(
        block_id=block.id,
        type=TRANSACTION_TYPE_VOTE,
        asset={
            "votes": [
                "+03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
            ]
        },
        sender_public_key=(
            "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
        ),
    )
    redis.set(
        "wallets:address:AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW",
        Wallet(
            {
                "address": "AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW",
                "public_key": (
                    "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
                ),
                "username": "spongebob",
                "vote_balance": 1,
                "balance": 4,
            }
        ).to_json(),
    )

    TransactionFactory(
        block_id=block.id,
        type=TRANSACTION_TYPE_VOTE,
        asset={
            "votes": [
                "+022eedf9f1cdae0cfaae635fe415b6a8f1912bc89bc3880ec41135d62cbbebd3d3"
            ]
        },
        sender_public_key=(
            "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
        ),
        timestamp=1234,
        sequence=1,
    )
    TransactionFactory(
        block_id=block.id,
        type=TRANSACTION_TYPE_VOTE,
        asset={
            "votes": [
                "+022eedf9f1cdae0cfaae635fe415b6a8f1912bc89bc3880ec41135d62cbbebd3d3"
            ]
        },
        sender_public_key=(
            "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
        ),
        timestamp=1234,
        sequence=2,
    )
    TransactionFactory(
        block_id=block.id,
        type=TRANSACTION_TYPE_VOTE,
        asset={
            "votes": [
                "+03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
            ]
        },
        sender_public_key=(
            "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
        ),
        timestamp=1234,
        sequence=0,
    )
    redis.set(
        "wallets:address:AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof",
        Wallet(
            {
                "address": "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof",
                "public_key": (
                    "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
                ),
                "balance": 1000,
            }
        ).to_json(),
    )

    TransactionFactory(
        block_id=block.id,
        type=TRANSACTION_TYPE_VOTE,
        asset={
            "votes": [
                "-03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
            ]
        },
        sender_public_key=(
            "022eedf9f1cdae0cfaae635fe415b6a8f1912bc89bc3880ec41135d62cbbebd3d3"
        ),
    )
    redis.set(
        "wallets:address:AcHFimRcEinGcJ1gBD3QAXKcFe8ZwNBkN7",
        Wallet(
            {
                "address": "AcHFimRcEinGcJ1gBD3QAXKcFe8ZwNBkN7",
                "public_key": (
                    "022eedf9f1cdae0cfaae635fe415b6a8f1912bc89bc3880ec41135d62cbbebd3d3"
                ),
                "balance": 1337,
            }
        ).to_json(),
    )

    TransactionFactory(
        block_id=block.id,
        type=TRANSACTION_TYPE_TRANSFER,
        amount=13000,
        fee=3000,
        sender_public_key=(
            "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
        ),
    )

    manager._build_votes()

    data_1 = json.loads(redis.get("wallets:address:AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW"))
    assert data_1["address"] == "AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW"
    assert (
        data_1["vote"]
        == "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
    )
    assert data_1["vote_balance"] == 1005
    assert data_1["balance"] == 4

    data_2 = json.loads(redis.get("wallets:address:AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof"))
    assert data_2["address"] == "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof"
    assert (
        data_2["vote"]
        == "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
    )
    assert data_2["balance"] == 1000

    data_3 = json.loads(redis.get("wallets:address:AcHFimRcEinGcJ1gBD3QAXKcFe8ZwNBkN7"))
    assert data_3["address"] == "AcHFimRcEinGcJ1gBD3QAXKcFe8ZwNBkN7"
    assert data_3["vote"] is None
    assert data_3["balance"] == 1337


def test_build_delegate(empty_db, redis):
    manager = WalletManager()
    block = BlockFactory(
        total_fee=10,
        reward=2,
        total_amount=12,
        generator_public_key=(
            "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
        ),
    )

    BlockFactory(
        total_fee=333,
        reward=666,
        total_amount=999,
        generator_public_key=(
            "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
        ),
    )

    TransactionFactory(
        block_id=block.id,
        type=TRANSACTION_TYPE_DELEGATE_REGISTRATION,
        asset={"delegate": {"username": "spongebob"}},
        sender_public_key=(
            "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
        ),
    )

    TransactionFactory(
        block_id=block.id,
        type=TRANSACTION_TYPE_TRANSFER,
        sender_public_key=(
            "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
        ),
    )

    manager._build_delegates()

    data = json.loads(redis.get("wallets:address:AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW"))
    assert data["address"] == "AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW"
    assert data["username"] == "spongebob"
    assert data["forged_fees"] == 343
    assert data["forged_rewards"] == 668
    assert data["produced_blocks"] == 2


def test_build_multi_signatures(empty_db, redis):
    manager = WalletManager()
    block = BlockFactory()
    multisig = {
        "multisignature": {
            "min": 2,
            "lifetime": 72,
            "keysgroup": [
                "034a7aca6841cfbdc688f09d55345f21c7ffbd1844693fa68d607fc94f729cbbea",
                "02fd6743ddfdc7c5bac24145e449c2e4f2d569b5297dd7bf088c3bc219f582a2f0",
            ],
        }
    }
    TransactionFactory(
        block_id=block.id,
        type=TRANSACTION_TYPE_MULTI_SIGNATURE,
        asset=multisig,
        sender_public_key=(
            "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
        ),
    )

    TransactionFactory(
        block_id=block.id,
        type=TRANSACTION_TYPE_TRANSFER,
        sender_public_key=(
            "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
        ),
    )

    manager._build_multi_signatures()

    data = json.loads(redis.get("wallets:address:AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW"))
    assert data["address"] == "AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW"
    assert (
        data["public_key"]
        == "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
    )
    assert data["multisignature"] == multisig["multisignature"]


def test_exists_returns_false_if_does_not_exist(redis):
    public_key = "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
    manager = WalletManager()
    assert manager.exists(public_key) is False


def test_exists_returns_true_if_exists(redis):
    manager = WalletManager()
    public_key = "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"

    redis.set("wallets:address:AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof", "")
    assert manager.exists(public_key) is True


def test_delegate_exists_returns_false_if_does_not_exist(redis):
    public_key = "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
    manager = WalletManager()
    assert manager.delegate_exists(public_key) is False


def test_delegate_exists_returns_true_if_exists(redis):
    manager = WalletManager()

    redis.set("wallets:username:test", "")
    assert manager.delegate_exists("test") is True


def test_is_delegate_returns_false_if_not_a_delegate(redis):
    public_key = "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
    manager = WalletManager()

    redis.set("wallets:address:AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof", json.dumps({}))
    assert manager.is_delegate(public_key) is False


def test_is_delegate_returns_true_if_is_delegate(redis):
    public_key = "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
    manager = WalletManager()

    redis.set(
        "wallets:address:AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof",
        json.dumps({"username": "test"}),
    )
    redis.set("wallets:username:test", "")
    assert manager.is_delegate(public_key) is True


def test_update_vote_balances_correctly_for_transaction_type_vote_plus(redis):
    manager = WalletManager()

    transaction = VoteTransaction()
    transaction.fee = 10000
    transaction.amount = 430000
    transaction.type = TRANSACTION_TYPE_VOTE
    transaction.asset = {
        "votes": ["+03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"]
    }

    redis.set(
        "wallets:address:AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW",
        json.dumps(
            {"address": "AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW", "vote_balance": 10000000}
        ),
    )

    sender = Wallet(
        {"address": "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof", "balance": 1337000}
    )

    manager._update_vote_balances(sender, None, transaction)

    delegate = json.loads(
        redis.get("wallets:address:AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW")
    )
    assert delegate["vote_balance"] == 11337000


def test_update_vote_balances_correctly_for_transaction_type_vote_plus_revert(redis):
    manager = WalletManager()

    transaction = VoteTransaction()
    transaction.fee = 10000
    transaction.amount = 430000
    transaction.type = TRANSACTION_TYPE_VOTE
    transaction.asset = {
        "votes": ["+03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"]
    }

    redis.set(
        "wallets:address:AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW",
        json.dumps(
            {"address": "AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW", "vote_balance": 10000000}
        ),
    )

    sender = Wallet(
        {"address": "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof", "balance": 1337000}
    )

    manager._update_vote_balances(sender, None, transaction, revert=True)

    delegate = json.loads(
        redis.get("wallets:address:AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW")
    )
    assert delegate["vote_balance"] == 8673000


def test_update_vote_balances_correctly_for_transaction_type_vote_minus(redis):
    manager = WalletManager()

    transaction = VoteTransaction()
    transaction.fee = 10000
    transaction.amount = 430000
    transaction.type = TRANSACTION_TYPE_VOTE
    transaction.asset = {
        "votes": ["-03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"]
    }

    redis.set(
        "wallets:address:AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW",
        json.dumps(
            {"address": "AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW", "vote_balance": 10000000}
        ),
    )

    sender = Wallet(
        {"address": "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof", "balance": 1337000}
    )

    manager._update_vote_balances(sender, None, transaction)

    delegate = json.loads(
        redis.get("wallets:address:AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW")
    )
    assert delegate["vote_balance"] == 8653000


def test_update_vote_balances_correctly_for_transaction_type_vote_minus_revert(redis):
    manager = WalletManager()

    transaction = VoteTransaction()
    transaction.fee = 10000
    transaction.amount = 430000
    transaction.type = TRANSACTION_TYPE_VOTE
    transaction.asset = {
        "votes": ["-03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"]
    }

    redis.set(
        "wallets:address:AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW",
        json.dumps(
            {"address": "AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW", "vote_balance": 10000000}
        ),
    )

    sender = Wallet(
        {"address": "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof", "balance": 1337000}
    )

    manager._update_vote_balances(sender, None, transaction, revert=True)

    delegate = json.loads(
        redis.get("wallets:address:AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW")
    )
    assert delegate["vote_balance"] == 11337000


def test_update_vote_balances_correctly_for_transaction(redis):
    manager = WalletManager()

    transaction = TransferTransaction()
    transaction.fee = 10000
    transaction.amount = 430000
    transaction.type = TRANSACTION_TYPE_TRANSFER

    redis.set(
        "wallets:address:AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW",
        json.dumps(
            {
                "address": "AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW",
                "public_key": (
                    "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
                ),
                "vote_balance": 10000000,
            }
        ),
    )
    redis.set(
        "wallets:address:AWoysqF1xm1LXYLQvmRDpfVNKzzaLVwPVM",
        json.dumps(
            {
                "address": "AWoysqF1xm1LXYLQvmRDpfVNKzzaLVwPVM",
                "public_key": (
                    "0316b3dc139c1a35927ecbdcb8d8b628ad06bd4f1869fe3ad0e23c8106678a460f"
                ),
                "vote_balance": 2000000,
            }
        ),
    )

    sender = Wallet(
        {
            "address": "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof",
            "public_key": (
                "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
            ),
            "balance": 1337000,
            "vote": (
                "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
            ),
        }
    )

    recipient = Wallet(
        {
            "address": "ASt5oBHKDW8AeJe2Ybc1RucMLS7mRCiuRe",
            "public_key": (
                "0316510c1409d3307d9f205cac58f1a871499c3ffea3878ddbbb48c821cfbc079a"
            ),
            "balance": 66000,
            "vote": (
                "0316b3dc139c1a35927ecbdcb8d8b628ad06bd4f1869fe3ad0e23c8106678a460f"
            ),
        }
    )

    manager._update_vote_balances(sender, recipient, transaction)

    delegate1 = json.loads(
        redis.get("wallets:address:AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW")
    )
    assert delegate1["vote_balance"] == 9560000

    delegate2 = json.loads(
        redis.get("wallets:address:AWoysqF1xm1LXYLQvmRDpfVNKzzaLVwPVM")
    )
    assert delegate2["vote_balance"] == 2430000


def test_update_vote_balances_correctly_for_transaction_revert(redis):
    manager = WalletManager()

    transaction = TransferTransaction()
    transaction.fee = 10000
    transaction.amount = 430000
    transaction.type = TRANSACTION_TYPE_TRANSFER

    redis.set(
        "wallets:address:AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW",
        json.dumps(
            {
                "address": "AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW",
                "public_key": (
                    "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
                ),
                "vote_balance": 10000000,
            }
        ),
    )
    redis.set(
        "wallets:address:AWoysqF1xm1LXYLQvmRDpfVNKzzaLVwPVM",
        json.dumps(
            {
                "address": "AWoysqF1xm1LXYLQvmRDpfVNKzzaLVwPVM",
                "public_key": (
                    "0316b3dc139c1a35927ecbdcb8d8b628ad06bd4f1869fe3ad0e23c8106678a460f"
                ),
                "vote_balance": 2000000,
            }
        ),
    )

    sender = Wallet(
        {
            "address": "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof",
            "public_key": (
                "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
            ),
            "balance": 1337000,
            "vote": (
                "03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2"
            ),
        }
    )

    recipient = Wallet(
        {
            "address": "ASt5oBHKDW8AeJe2Ybc1RucMLS7mRCiuRe",
            "public_key": (
                "0316510c1409d3307d9f205cac58f1a871499c3ffea3878ddbbb48c821cfbc079a"
            ),
            "balance": 66000,
            "vote": (
                "0316b3dc139c1a35927ecbdcb8d8b628ad06bd4f1869fe3ad0e23c8106678a460f"
            ),
        }
    )

    manager._update_vote_balances(sender, recipient, transaction, revert=True)

    delegate1 = json.loads(
        redis.get("wallets:address:AZYnpgXS3x43nxqhT4q29sZScRwZeNKLpW")
    )
    assert delegate1["vote_balance"] == 10440000

    delegate2 = json.loads(
        redis.get("wallets:address:AWoysqF1xm1LXYLQvmRDpfVNKzzaLVwPVM")
    )
    assert delegate2["vote_balance"] == 1570000
