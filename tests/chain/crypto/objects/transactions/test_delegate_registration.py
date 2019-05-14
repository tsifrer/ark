from chain.crypto.constants import TRANSACTION_TYPE_DELEGATE_REGISTRATION
from chain.crypto.models.wallet import Wallet
from chain.crypto.objects.transactions.delegate_registration import (
    DelegateRegistrationTransaction,
)
from chain.plugins.database.wallet_manager import WalletManager

from tests.chain.factories import PoolTransactionFactory


def test_can_be_applied_to_wallet_returns_false_if_username_is_not_set():
    transaction = DelegateRegistrationTransaction()
    transaction.asset = {"delegate": {"username": ""}}
    can_apply = transaction.can_be_applied_to_wallet(None, None, None)
    assert can_apply is False


def test_can_be_applied_to_wallet_returns_false_if_delegate_already_exist(mocker):
    transaction = DelegateRegistrationTransaction()
    transaction.asset = {"delegate": {"username": "harambe"}}

    manager = mocker.Mock()
    manager.delegate_exists = lambda x: True
    can_apply = transaction.can_be_applied_to_wallet(None, manager, None)
    assert can_apply is False


def test_can_be_applied_to_wallet_calls_super(mocker):
    transaction = DelegateRegistrationTransaction()
    transaction.asset = {"delegate": {"username": "harambe"}}

    super_mock = mocker.patch(
        (
            "chain.crypto.objects.transactions.delegate_registration.BaseTransaction."
            "can_be_applied_to_wallet"
        ),
        return_value=True,
    )
    manager = mocker.Mock()
    manager.delegate_exists = lambda x: False

    can_apply = transaction.can_be_applied_to_wallet(None, manager, None)
    assert can_apply is True
    assert super_mock.call_count == 1


def test_appply_to_sender_wallet(mocker):
    transaction = DelegateRegistrationTransaction()
    transaction.asset = {"delegate": {"username": "harambe"}}
    wallet = Wallet({})

    super_mock = mocker.patch(
        "chain.crypto.objects.transactions.delegate_registration.BaseTransaction."
        "apply_to_sender_wallet"
    )

    transaction.apply_to_sender_wallet(wallet)
    assert super_mock.call_count == 1
    assert wallet.username == "harambe"


def test_revert_for_sender_wallet(mocker):
    transaction = DelegateRegistrationTransaction()
    transaction.asset = {"delegate": {"username": "harambe"}}
    wallet = Wallet({"username": "harambe"})

    super_mock = mocker.patch(
        "chain.crypto.objects.transactions.delegate_registration.BaseTransaction."
        "revert_for_sender_wallet"
    )

    transaction.revert_for_sender_wallet(wallet)
    assert super_mock.call_count == 1
    assert wallet.username is None


def test_apply(redis, mocker):
    transaction = DelegateRegistrationTransaction()
    manager = WalletManager()
    sender_wallet = Wallet(
        {"address": "AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof", "username": "harambe"}
    )
    transaction.apply(sender_wallet, None, manager)

    data = redis.get("wallets:username:harambe")

    assert data == b"AThM5PNSKdU9pu1ydqQnzRWVeNCGr8HKof"


def test_validate_for_transaction_pool_returns_error_for_existing_type(mocker):
    transaction = DelegateRegistrationTransaction()
    transaction.sender_public_key = (
        "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
    )
    transaction.type = TRANSACTION_TYPE_DELEGATE_REGISTRATION

    pool = mocker.Mock()
    pool.sender_has_transactions_of_type = lambda x: True

    response = transaction.validate_for_transaction_pool(pool, None)
    assert response == (
        "Sender 020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325 "
        "already has a transaction of type 2 in the pool"
    )


def test_validate_for_transaction_pool_returns_error_if_duplicate_transactions(mocker):
    transaction = DelegateRegistrationTransaction()
    transaction.asset = {"delegate": {"username": "harambe"}}

    transaction1 = DelegateRegistrationTransaction()
    transaction1.asset = {"delegate": {"username": "harambe"}}

    pool = mocker.Mock()
    pool.sender_has_transactions_of_type = lambda x: False
    response = transaction.validate_for_transaction_pool(
        pool, [transaction, transaction1]
    )
    assert response == (
        "Multiple delegate registrations for harambe in transaction payload"
    )


def test_validate_for_transaction_pool_returns_error_if_transaction_exists(
    empty_db, mocker
):
    transaction = DelegateRegistrationTransaction()
    transaction.asset = {"delegate": {"username": "harambe"}}
    transaction.type = TRANSACTION_TYPE_DELEGATE_REGISTRATION

    PoolTransactionFactory(
        type=TRANSACTION_TYPE_DELEGATE_REGISTRATION,
        asset={"delegate": {"username": "harambe"}},
    )

    pool = mocker.Mock()
    pool.sender_has_transactions_of_type = lambda x: False
    response = transaction.validate_for_transaction_pool(pool, [transaction])
    assert response == "Delegate registration for harambe already in the pool"


def test_validate_for_transaction_pool(mocker):
    transaction = DelegateRegistrationTransaction()
    transaction.asset = {"delegate": {"username": "harambe"}}
    transaction.type = TRANSACTION_TYPE_DELEGATE_REGISTRATION

    pool = mocker.Mock()
    pool.sender_has_transactions_of_type = lambda x: False
    response = transaction.validate_for_transaction_pool(pool, [transaction])
    assert response is None
