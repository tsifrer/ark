from chain.crypto.models.wallet import Wallet
from chain.crypto.objects.transactions.multi_signature import MultiSignatureTransaction


def test_verify_signatures_returns_false_if_signature_len_is_smaller_than_min():
    transaction = MultiSignatureTransaction()
    transaction.asset = {"multisignature": {"min": 5}}
    transaction.signatures = ["a"]
    verified = transaction._verify_signatures()
    assert verified is False


def test_can_be_applied_to_wallet_returns_false_if_multisig_is_already_set():
    transaction = MultiSignatureTransaction()
    wallet = Wallet({"multisignature": "abcd"})
    can_apply = transaction.can_be_applied_to_wallet(wallet, None, None)
    assert can_apply is False


def test_can_be_applied_to_wallet_returns_false_if_multisig_wrong_length():
    transaction = MultiSignatureTransaction()
    transaction.asset = {"multisignature": {"keysgroup": ["abcd"], "min": 5}}
    wallet = Wallet({})
    can_apply = transaction.can_be_applied_to_wallet(wallet, None, None)
    assert can_apply is False


def test_can_be_applied_to_wallet_returns_false_if_signatures_len_is_wrong():
    transaction = MultiSignatureTransaction()
    transaction.asset = {"multisignature": {"keysgroup": ["abcd"], "min": 1}}
    transaction.signatures = ["a", "b"]
    wallet = Wallet({})
    can_apply = transaction.can_be_applied_to_wallet(wallet, None, None)
    assert can_apply is False


def test_appply_to_sender_wallet(mocker):
    transaction = MultiSignatureTransaction()
    transaction.asset = {"multisignature": {"keysgroup": ["abcd"], "min": 1}}
    wallet = Wallet({})

    super_mock = mocker.patch(
        "chain.crypto.objects.transactions.multi_signature.BaseTransaction."
        "apply_to_sender_wallet"
    )

    transaction.apply_to_sender_wallet(wallet)
    assert super_mock.call_count == 1
    assert wallet.multisignature == {"keysgroup": ["abcd"], "min": 1}


def test_revert_for_sender_wallet(mocker):
    transaction = MultiSignatureTransaction()
    transaction.asset = {"delegate": {"username": "harambe"}}
    wallet = Wallet({"multisignature": {"keysgroup": ["abcd"], "min": 1}})

    super_mock = mocker.patch(
        "chain.crypto.objects.transactions.multi_signature.BaseTransaction."
        "revert_for_sender_wallet"
    )

    transaction.revert_for_sender_wallet(wallet)
    assert super_mock.call_count == 1
    assert wallet.username is None
