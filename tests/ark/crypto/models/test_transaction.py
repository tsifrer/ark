from binascii import hexlify

from ark.crypto.models.transaction import Transaction

# TODO: MOARD TESTS!!!


def test_serialize_correctly_serializes_transaction(
    dummy_transaction, dummy_transaction_hash
):
    transaction = Transaction(dummy_transaction)
    serialized = transaction.serialize()
    assert serialized == dummy_transaction_hash


def test_get_bytes_returns_correct_data():
    data = {
        'type': 0,
        'amount': 1000,
        'fee': 2000,
        'recipientId': 'AJWRd23HNEhPLkK1ymMnwnDBX2a7QBZqff',
        'timestamp': 141738,
        'asset': {},
        'senderPublicKey': '5d036a858ce89f844491762eb89e2bfbd50a4a0a0da658e4b2628b25b117ae09',
        'signature':
            '618a54975212ead93df8c881655c625544bce8ed7ccdfe6f08a42eecfb1adebd051307be5014bb051617baf7815d50f62129e70918190361e5d4dd4796541b0a',
        'id': '13987348420913138422',
    }

    transaction = Transaction(data)
    bytes_data = transaction.get_bytes()
    assert isinstance(bytes_data, bytes)
    assert len(bytes_data) == 202
    assert hexlify(bytes_data) == b'00aa2902005d036a858ce89f844491762eb89e2bfbd50a4a0a0da658e4b2628b25b117ae09171dfc69b54c7fe901e91d5a9ab78388645e2427ea00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e803000000000000d007000000000000618a54975212ead93df8c881655c625544bce8ed7ccdfe6f08a42eecfb1adebd051307be5014bb051617baf7815d50f62129e70918190361e5d4dd4796541b0a'



def test_bla():
    data = {
        'type': 0,
        'amount': 1000,
        'fee': 2000,
        'recipientId': 'AJWRd23HNEhPLkK1ymMnwnDBX2a7QBZqff',
        'timestamp': 141738,
        'asset': {},
        'senderPublicKey': '03d04acca0ad922998d258438cc453ce50222b0e761ae9a499ead6a11f3a44b70b',
        'signature':
            '3045022100f5c4ec7b3f9a2cb2e785166c7ae185abbff0aa741cbdfe322cf03b914002efee02206261cd419ea9074b5d4a007f1e2fffe17a38338358f2ac5fcc65d810dbe773fe',
        # 'id': '13987348420913138422',
    }

    transaction = Transaction(data)
    print(transaction.verify())




# def test_omg():
#     data = {
#         'version': 1,
#         'network': 30,
#         'type': 0,
#         'timestamp': 45021209,
#         'senderPublicKey': '03d3fdad9c5b25bf8880e6b519eb3611a5c0b31adebc8455f0e096175b28321aff',
#         'fee': 10000000,
#         'amount': 5100000000,
#         'expiration': 0,
#         'recipientId': 'D8vKwaX6ksU3mWg7tJDm7v1dbxy4cMo4dh',
#         'signature': '3045022100f6914de508a19326148f3774456508270607fc2bee6c56acb2f7e2eb6999179c022043f9005f7d254bb0ecff2a14b035fc8aa83bd0e55135ff8c3181993606f2efe5',
#         'id': '35904cf41b4df8f2e45d1aac366eca8fce25118d19b94333502cc66973adc815',
#         'blockId': '10172429794310518146'
#       }

#     transaction = Transaction(data)
#     print(len(transaction.get_bytes()))
#     print(transaction.verify())
