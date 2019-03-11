from binascii import hexlify

from chain.crypto.models.transaction import Transaction

# TODO: MOARD TESTS!!!

def test_omg(dummy_transaction, dummy_transaction_hash):
    transaction = Transaction(dummy_transaction_hash)
    # serialized = transaction.serialize()


# def test_serialize_correctly_serializes_transaction(
#     dummy_transaction, dummy_transaction_hash
# ):
#     transaction = Transaction(dummy_transaction)
#     serialized = transaction.serialize()
#     assert serialized == dummy_transaction_hash


# def test_get_bytes_returns_correct_data():
#     data = {
#         'type': 0,
#         'amount': 1000,
#         'fee': 2000,
#         'recipientId': 'AJWRd23HNEhPLkK1ymMnwnDBX2a7QBZqff',
#         'timestamp': 141738,
#         'asset': {},
#         'senderPublicKey': (
#             '5d036a858ce89f844491762eb89e2bfbd50a4a0a0da658e4b2628b25b117ae09'
#         ),
#         'signature': (
#             '618a54975212ead93df8c881655c625544bce8ed7ccdfe6f08a42eecfb1adebd051307be50'
#             '14bb051617baf7815d50f62129e70918190361e5d4dd4796541b0a'
#         ),
#         'id': '13987348420913138422',
#     }

#     transaction = Transaction(data)
#     bytes_data = transaction.get_bytes()
#     assert isinstance(bytes_data, bytes)
#     assert len(bytes_data) == 202
#     assert hexlify(bytes_data) == (
#         b'00aa2902005d036a858ce89f844491762eb89e2bfbd50a4a0a0da658e4b2628b25b117ae09171'
#         b'dfc69b54c7fe901e91d5a9ab78388645e2427ea00000000000000000000000000000000000000'
#         b'00000000000000000000000000000000000000000000000000000000000000000000000000000'
#         b'0000000000000e803000000000000d007000000000000618a54975212ead93df8c881655c6255'
#         b'44bce8ed7ccdfe6f08a42eecfb1adebd051307be5014bb051617baf7815d50f62129e70918190'
#         b'361e5d4dd4796541b0a'
#     )


# def test_verify_correctly_verifies_the_transaction():
#     data = {
#         'version': 1,
#         'network': 30,
#         'type': 0,
#         'timestamp': 45021209,
#         'senderPublicKey': (
#             '03d3fdad9c5b25bf8880e6b519eb3611a5c0b31adebc8455f0e096175b28321aff'
#         ),
#         'fee': 10000000,
#         'amount': 5100000000,
#         'expiration': 0,
#         'recipientId': 'D8vKwaX6ksU3mWg7tJDm7v1dbxy4cMo4dh',
#         'signature': (
#             '3045022100f6914de508a19326148f3774456508270607fc2bee6c56acb2f7e2eb6999179c'
#             '022043f9005f7d254bb0ecff2a14b035fc8aa83bd0e55135ff8c3181993606f2efe5'
#         ),
#         'id': '35904cf41b4df8f2e45d1aac366eca8fce25118d19b94333502cc66973adc815',
#         'blockId': '10172429794310518146',
#     }
#     transaction = Transaction(data)
#     assert transaction.verify() is True


# def test_omg():
#     data = {
#         'id': '656383382263774702',
#         'version': 0,
#         'timestamp': 60302426,
#         'height': 1554984,
#         'reward': '200000000',
#         'previousBlock': '6583834412064820799',
#         'numberOfTransactions': 0,
#         'totalAmount': '0',
#         'totalFee': '0',
#         'payloadLength': 0,
#         'payloadHash': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
#         'generatorPublicKey': '03d7a20b3d39b7526a5057a9b486f0200bc57543e69e5fa61d9ce0bdd7784162c3',
#         'blockSignature': '30450221009e477e36062129cf2ffb21e24e460231af701cf352e57a0f83470dc24f1edcfb022054e55f8b246d3d775a9267ea6e3f9ba2add1618b20b087586f7df7812b2e0953',
#     }
#     transaction = Transaction(data)
#     assert transaction.verify() is True
