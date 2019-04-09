import pytest

from chain.plugins.transaction_pool.utils import is_recipient_on_current_network


@pytest.mark.parametrize(
    "recipient_id,expected",
    [
        ("AJWRd23HNEhPLkK1ymMnwnDBX2a7QBZqff", True),
        ("DEJHR83JFmGpXYkJiaqn7wPGztwjheLAmY", False),
    ],
)
def test_is_recipient_on_current_network(recipient_id, expected):
    result = is_recipient_on_current_network(recipient_id)
    assert result == expected
