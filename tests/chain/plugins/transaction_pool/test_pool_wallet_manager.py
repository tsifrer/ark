import json

import pytest

from chain.crypto.models.wallet import Wallet
from chain.plugins.transaction_pool.pool_wallet_manager import PoolWalletManager


def test_key_for_address():
    manager = PoolWalletManager()
    key = manager.key_for_address("spongebob")
    assert key == "pool_wallet:address:spongebob"


def test_clear_wallets(redis):
    manager = PoolWalletManager()
    redis.set("pool_wallet:address:spongebob", "1")
    redis.set("pool_wallet:address:squarepants", "2")
    assert len(redis.keys("pool_wallet:address:*")) == 2
    manager.clear_wallets()
    assert len(redis.keys("pool_wallet:address:*")) == 0


def test_save_wallet(redis):
    manager = PoolWalletManager()
    wallet = Wallet({"address": "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof"})
    manager.save_wallet(wallet)
    data = json.loads(
        redis.get("pool_wallet:address:AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof")
    )
    assert data["address"] == wallet.address


def test_find_by_address_copies_wallet_from_blockchain_wallet_manager(redis):
    manager = PoolWalletManager()

    chain_wallet = Wallet(
        {"address": "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof", "username": "spongebob"}
    )
    redis.set(
        "wallets:address:AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof", chain_wallet.to_json()
    )
    wallet = manager.find_by_address("AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof")

    assert redis.exists("pool_wallet:address:AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof")
    assert wallet.to_json() == chain_wallet.to_json()


def test_find_by_address_returns_existin_wallet_from_redis(redis):
    manager = PoolWalletManager()

    existing_wallet = Wallet(
        {"address": "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof", "username": "spongebob"}
    )
    redis.set(
        "pool_wallet:address:AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof",
        existing_wallet.to_json(),
    )
    wallet = manager.find_by_address("AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof")
    assert len(redis.keys("pool_wallet:address:*")) == 1
    assert wallet.to_json() == existing_wallet.to_json()


def test_find_by_public_key_copies_wallet_from_blockchain_wallet_manager(redis):
    manager = PoolWalletManager()

    chain_wallet = Wallet(
        {"address": "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof", "username": "spongebob"}
    )
    redis.set(
        "wallets:address:AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof", chain_wallet.to_json()
    )
    wallet = manager.find_by_public_key(
        "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
    )

    assert redis.exists("pool_wallet:address:AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof")
    assert wallet.to_json() == chain_wallet.to_json()


def test_find_by_public_key_returns_existin_wallet_from_redis(redis):
    manager = PoolWalletManager()

    existing_wallet = Wallet(
        {"address": "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof", "username": "spongebob"}
    )
    redis.set(
        "pool_wallet:address:AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof",
        existing_wallet.to_json(),
    )
    wallet = manager.find_by_public_key(
        "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
    )
    assert len(redis.keys("pool_wallet:address:*")) == 1
    assert wallet.to_json() == existing_wallet.to_json()


@pytest.mark.parametrize(
    "address,expected",
    [("AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof", True), ("spongebob", False)],
)
def test_exists_by_address(address, expected, redis):
    manager = PoolWalletManager()
    redis.set("pool_wallet:address:AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof", "1337")
    assert manager.exists_by_address(address) == expected


@pytest.mark.parametrize(
    "public_key,expected",
    [
        ("020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325", True),
        ("03b12f99375c3b0e4f5f5c7ea74e723f0b84a6f169b47d9105ed2a179f30c82df2", False),
    ],
)
def test_exists_by_public_key(public_key, expected, redis):
    manager = PoolWalletManager()
    redis.set("pool_wallet:address:AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof", "1337")

    assert manager.exists_by_public_key(public_key) == expected


def test_delete_by_public_key(redis):
    manager = PoolWalletManager()
    redis.set("pool_wallet:address:AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof", "1337")

    manager.delete_by_public_key(
        "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
    )
    assert redis.exists("pool_wallet:address:AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof") == 0


def test_can_apply_to_sender_returns_true_if_everything_ok(redis, crypto_transaction):
    manager = PoolWalletManager()
    chain_wallet = Wallet(
        {"address": "AS2YSSDbbXBAehfbm1KAEvJMJFdPPT2aRT", "balance": 133700000}
    )
    redis.set(
        "wallets:address:AS2YSSDbbXBAehfbm1KAEvJMJFdPPT2aRT", chain_wallet.to_json()
    )
    crypto_transaction.second_signature = None
    crypto_transaction.sign_signature = None
    can_apply = manager.can_apply_to_sender(crypto_transaction, 2243161)
    assert can_apply is True


def test_can_apply_to_sender_returns_true_if_transaction_is_exception(
    redis, crypto_transaction, mocker
):
    manager = PoolWalletManager()

    exception_mock = mocker.patch(
        "chain.plugins.transaction_pool.pool_wallet_manager.is_transaction_exception",
        return_value=True,
    )
    chain_wallet = Wallet(
        {"address": "AMm7u2Kpaf3gY2Y96MovudH2q65WHi8Sqd", "balance": 133700000}
    )
    redis.set(
        "wallets:address:AMm7u2Kpaf3gY2Y96MovudH2q65WHi8Sqd", chain_wallet.to_json()
    )

    can_apply = manager.can_apply_to_sender(crypto_transaction, 2243161)
    assert can_apply is True
    exception_mock.assert_called_once_with(crypto_transaction.id)


def test_can_apply_to_sender_returns_false_if_balance_is_zero(
    redis, crypto_transaction
):
    manager = PoolWalletManager()

    chain_wallet = Wallet(
        {"address": "AMm7u2Kpaf3gY2Y96MovudH2q65WHi8Sqd", "balance": 0}
    )
    redis.set(
        "wallets:address:AMm7u2Kpaf3gY2Y96MovudH2q65WHi8Sqd", chain_wallet.to_json()
    )

    can_apply = manager.can_apply_to_sender(crypto_transaction, 2243161)
    assert can_apply is False
