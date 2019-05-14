import pytest

from chain.crypto.objects.transactions import (
    TransferTransaction,
    from_dict,
    from_object,
    from_serialized,
)


def test_from_serialized(dummy_transaction_hash):
    transaction = from_serialized(dummy_transaction_hash)
    assert isinstance(transaction, TransferTransaction)
    assert (
        transaction.id
        == "f861b25c9a87fc8913282da8855ee63b9cbaa9324543377a5bdfc5afccb92aaa"
    )


def test_from_serialized_raises_type_error_if_hex_not_bytes():
    with pytest.raises(TypeError) as excinfo:
        from_serialized("not_bytes")
    assert str(excinfo.value) == "serialized_hex must be bytes"


def test_from_serialized_raises_value_error_if_transaction_type_does_not_exist():
    serialized_hex = b"ffffff7b"
    with pytest.raises(ValueError) as excinfo:
        from_serialized(serialized_hex)
    assert str(excinfo.value) == "Couldn't find transaction type 123 in mapping"


def test_from_dict(dummy_transaction):
    transaction = from_dict(dummy_transaction)
    assert isinstance(transaction, TransferTransaction)
    assert (
        transaction.id
        == "f861b25c9a87fc8913282da8855ee63b9cbaa9324543377a5bdfc5afccb92aaa"
    )


def test_from_dict_raises_type_error_if_data_not_dict():
    with pytest.raises(TypeError) as excinfo:
        from_dict("not_dict")
    assert str(excinfo.value) == "data must be dict"


def test_from_dict_raises_value_error_if_transaction_type_does_not_exist(
    dummy_transaction
):
    dummy_transaction["type"] = 123
    with pytest.raises(ValueError) as excinfo:
        from_dict(dummy_transaction)
    assert str(excinfo.value) == "Couldn't find transaction type 123 in mapping"


def test_from_object(crypto_transaction):
    transaction = from_object(crypto_transaction)
    assert isinstance(transaction, TransferTransaction)
    assert (
        transaction.id
        == "f861b25c9a87fc8913282da8855ee63b9cbaa9324543377a5bdfc5afccb92aaa"
    )


def test_from_object_raises_value_error_if_transaction_type_does_not_exist(
    crypto_transaction
):
    crypto_transaction.type = 123
    with pytest.raises(ValueError) as excinfo:
        from_object(crypto_transaction)
    assert str(excinfo.value) == "Couldn't find transaction type 123 in mapping"
