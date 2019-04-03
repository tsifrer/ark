import pytest

from chain.crypto.objects.block import Block
from chain.crypto.objects.transaction import Transaction


@pytest.fixture
def dummy_block_full_hash():
    return (
        "0000000078d07901593a22002b324b8b33a85802070000007c5c3b0000000000801d2c04000000"
        "0000c2eb0b00000000e00000003784b953afcf936bdffd43fdf005b5732b49c1fc6b11e195c364"
        "c20b2eb06282020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
        "3045022100eee6c37b5e592e99811d588532726353592923f347c701d52912e6d583443e400220"
        "277ffe38ad31e216ba0907c4738fed19b2071246b150c72c0a52bae4477ebe29ff000000fe0000"
        "0000010000ff000000ff000000ff000000ff000000ff011e0062d079010265c1f6b8c1966a90f3"
        "fed7bc32fd4f42238ab4938fdb2a4e7ddd01ae8b58b4c080969800000000001f476f6f73652056"
        "6f746572202d205472756520426c6f636b20576569676874f07a080000000000000000001e40fa"
        "d23d21da7a4fd4decb5c49726ea22f5e6bf6304402204f12469157b19edd06ba25fcad3d4a5ef5"
        "b057c23f9e02de4641e6f8eef0553e022010121ab282f83efe1043de9c16bbf2c6845a03684229"
        "a0d7c965ffb9abdfb97830450221008327862f0b9178d6665f7d6674978c5caf749649558d8142"
        "44b1c66cdf945c40022015918134ef01fed3fe2a2efde3327917731344332724522c75c2799a14"
        "f78717ff011e0060d079010265c1f6b8c1966a90f3fed7bc32fd4f42238ab4938fdb2a4e7ddd01"
        "ae8b58b4c080969800000000001f476f6f736520566f746572202d205472756520426c6f636b20"
        "576569676874e67a080000000000000000001e79c579fb08f448879c22fe965906b4e3b88d02ed"
        "304402205f82feb8c5d1d79c565c2ff7badb93e4c9827b132d135dda11cb25427d4ef8ac02205f"
        "f136f970533c4ec4c7d0cd1ea7e02d7b62629b66c6c93265f608d7f2389727304402207e912031"
        "fcc700d8a55fbc415993302a0d8e6aea128397141b640b6dba52331702201fd1ad3984e42af44f"
        "548907add6cb7ad72ca0070c8cc1d8dc9bbda208c56bd9ff011e0064d079010265c1f6b8c1966a"
        "90f3fed7bc32fd4f42238ab4938fdb2a4e7ddd01ae8b58b4c080969800000000001f476f6f7365"
        "20566f746572202d205472756520426c6f636b20576569676874fa7a080000000000000000001e"
        "84fee45dde2b11525afe192a2e991d014ff93a36304502210083216e6969e068770e6d2fe5c244"
        "881002309df84d20290ddf3f858967ed010202202a479b3da5080ea475d310ff13494654b42db7"
        "5886a8808bd211b4bdb9146a7a3045022100e1dcab3406bbeb968146a4a391909ce41df9b71592"
        "a753b001e7c2ee1d382c5102202a74aeafd4a152ec61854636fbae829c41f1416c1e0637a08094"
        "08394973099fff011e0061d079010265c1f6b8c1966a90f3fed7bc32fd4f42238ab4938fdb2a4e"
        "7ddd01ae8b58b4c080969800000000001f476f6f736520566f746572202d205472756520426c6f"
        "636b20576569676874e67a080000000000000000001e1d69583ede5ee82d220e74bffb36bae2ce"
        "762dfb3045022100cd4fa9855227be11e17201419dacfbbd5d9946df8d6792a948816002569382"
        "1402207fb83969bad6a26959f437b5bb88e255b0a48eb04964d0c0d29f7ee94bd15e1130440220"
        "5f50c2991a17743d17ffbb09159cadc35a3f848044261842879ccf5be9d81c5e022023bf21c32f"
        "b6e94494104f15f8d3a942ab120d0abd6fb4c93790b68e1b307a79ff011e0062d079010265c1f6"
        "b8c1966a90f3fed7bc32fd4f42238ab4938fdb2a4e7ddd01ae8b58b4c080969800000000001f47"
        "6f6f736520566f746572202d205472756520426c6f636b20576569676874f07a08000000000000"
        "0000001e56f9a37a859f4f84e93ce7593e809b15a524db2930450221009c792062e13399ac6756"
        "b2e9f137194d06e106360ac0f3e24e55c7249cee0b3602205dc1d9c76d0451d1cb5a2396783a13"
        "e6d2d790ccfd49291e3d0a78349f7ea0e830440220083ba8a9af49b8be6e93794d71ec43ffc96a"
        "158375810e5d9f2478e71655315b0220278402ecaa1d224dab9f0f3b28295bbaea339c85c7400e"
        "dafdc49df87439fc64ff011e0063d079010265c1f6b8c1966a90f3fed7bc32fd4f42238ab4938f"
        "db2a4e7ddd01ae8b58b4c080969800000000001f476f6f736520566f746572202d205472756520"
        "426c6f636b20576569676874f07a080000000000000000001e0232a083c16aba4362dddec1b305"
        "0ffdd6d43f2e3044022063c65263e42be02bd9831b375c1d76a88332f00ed0557ecc1e7d2375ca"
        "40070902206797b5932c0bad68444beb5a38daa7cadf536ee2144e0d9777b812284d14374e3045"
        "022100b04da6692f75d43229ffd8486c1517e8952d38b4c03dfac38b6b360190a5c33e02207766"
        "22e5f09f92a1258b4a011f22181c977b622b8d1bbb2f83b42f4126d00739ff011e0060d0790102"
        "65c1f6b8c1966a90f3fed7bc32fd4f42238ab4938fdb2a4e7ddd01ae8b58b4c080969800000000"
        "001f476f6f736520566f746572202d205472756520426c6f636b20576569676874e67a08000000"
        "0000000000001eccc4fce0dc95f9951ee40c09a7ae807746cf51403045022100d4513c3608c207"
        "2e38e7a0e3bb8daf2cd5f7cc6fec9a5570dccd1eda696c591902202ecbbf3c9d0757be7b23c8b1"
        "cc6481c51600d158756c47fcb6f4a7f4893e31c4304402201fed4858d0806dd32220960900a871"
        "dd2f60e1f623af75feef9b1034a9a0a46402205a29b27c63fcc3e1ee1e77ecbbf4dd6e7db09901"
        "e7a09b9fd490cd68d62392cb"
    ).encode("utf-8")


@pytest.fixture
def dummy_block_hash():
    return (
        "0000000078d07901593a22002b324b8b33a85802070000007c5c3b0000000000801d2c04000000"
        "0000c2eb0b00000000e00000003784b953afcf936bdffd43fdf005b5732b49c1fc6b11e195c364"
        "c20b2eb06282020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
        "3045022100eee6c37b5e592e99811d588532726353592923f347c701d52912e6d583443e400220"
        "277ffe38ad31e216ba0907c4738fed19b2071246b150c72c0a52bae4477ebe29"
    ).encode("utf-8")


@pytest.fixture
def dummy_transaction_hash():
    return (
        "ff011e0062d079010265c1f6b8c1966a90f3fed7bc32fd4f42238ab4938fdb2a4e7ddd01ae8b58"
        "b4c080969800000000001f476f6f736520566f746572202d205472756520426c6f636b20576569"
        "676874f07a080000000000000000001e40fad23d21da7a4fd4decb5c49726ea22f5e6bf6304402"
        "204f12469157b19edd06ba25fcad3d4a5ef5b057c23f9e02de4641e6f8eef0553e022010121ab2"
        "82f83efe1043de9c16bbf2c6845a03684229a0d7c965ffb9abdfb97830450221008327862f0b91"
        "78d6665f7d6674978c5caf749649558d814244b1c66cdf945c40022015918134ef01fed3fe2a2e"
        "fde3327917731344332724522c75c2799a14f78717"
    ).encode("utf-8")


@pytest.fixture
def dummy_transaction():
    return {
        "type": 0,
        "amount": 555760,
        "fee": 10000000,
        "recipientId": "DB4gFuDztmdGALMb8i1U4Z4R5SktxpNTAY",
        "timestamp": 24760418,
        "asset": {},
        "vendorField": "Goose Voter - True Block Weight",
        "senderPublicKey": (
            "0265c1f6b8c1966a90f3fed7bc32fd4f42238ab4938fdb2a4e7ddd01ae8b58b4c0"
        ),
        "signature": (
            "304402204f12469157b19edd06ba25fcad3d4a5ef5b057c23f9e02de4641e6f8ee"
            "f0553e022010121ab282f83efe1043de9c16bbf2c6845a03684229a0d7c965ffb9"
            "abdfb978"
        ),
        "signSignature": (
            "30450221008327862f0b9178d6665f7d6674978c5caf749649558d814244b1c66c"
            "df945c40022015918134ef01fed3fe2a2efde3327917731344332724522c75c279"
            "9a14f78717"
        ),
        "id": "170543154a3b79459cbaa529f9f62b6f1342682799eb549dbf09fcca2d1f9c11",
        "senderId": "DB8LnnQqYvHpG4WkGJ9AJWBYEct7G3yRZg",
        "hop": 2,
        "broadcast": False,
        "blockId": "7176646138626297930",
    }


@pytest.fixture
def dummy_block(dummy_transaction):
    return {
        "id": "7176646138626297930",
        "version": 0,
        "height": 2243161,
        "timestamp": 24760440,
        "previousBlock": "3112633353705641986",
        "numberOfTransactions": 7,
        "totalAmount": "3890300",
        "totalFee": "70000000",
        "reward": "200000000",
        "payloadLength": 224,
        "payloadHash": (
            "3784b953afcf936bdffd43fdf005b5732b49c1fc6b11e195c364c20b2eb06282"
        ),
        "generatorPublicKey": (
            "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
        ),
        "blockSignature": (
            "3045022100eee6c37b5e592e99811d588532726353592923f347c701d52912e6d583443e40"
            "0220277ffe38ad31e216ba0907c4738fed19b2071246b150c72c0a52bae4477ebe29"
        ),
        "transactions": [
            dummy_transaction,
            {
                "type": 0,
                "amount": 555750,
                "fee": 10000000,
                "recipientId": "DGExsNogZR7JFa2656ZFP9TMWJYJh5djzQ",
                "timestamp": 24760416,
                "asset": {},
                "vendorField": "Goose Voter - True Block Weight",
                "senderPublicKey": (
                    "0265c1f6b8c1966a90f3fed7bc32fd4f42238ab4938fdb2a4e7ddd01ae8b58b4c0"
                ),
                "signature": (
                    "304402205f82feb8c5d1d79c565c2ff7badb93e4c9827b132d135dda11cb25427d"
                    "4ef8ac02205ff136f970533c4ec4c7d0cd1ea7e02d7b62629b66c6c93265f608d7"
                    "f2389727"
                ),
                "signSignature": (
                    "304402207e912031fcc700d8a55fbc415993302a0d8e6aea128397141b640b6dba"
                    "52331702201fd1ad3984e42af44f548907add6cb7ad72ca0070c8cc1d8dc9bbda2"
                    "08c56bd9"
                ),
                "id": (
                    "1da153f37eceda233ff1b407ac18e47b3cae47c14cdcd5297d929618a916c4a7"
                ),
                "senderId": "DB8LnnQqYvHpG4WkGJ9AJWBYEct7G3yRZg",
                "hop": 2,
                "broadcast": False,
                "blockId": "7176646138626297930",
            },
            {
                "type": 0,
                "amount": 555770,
                "fee": 10000000,
                "recipientId": "DHGK5np6LuMMErfRfC5CmjpGu3ME85c25n",
                "timestamp": 24760420,
                "asset": {},
                "vendorField": "Goose Voter - True Block Weight",
                "senderPublicKey": (
                    "0265c1f6b8c1966a90f3fed7bc32fd4f42238ab4938fdb2a4e7ddd01ae8b58b4c0"
                ),
                "signature": (
                    "304502210083216e6969e068770e6d2fe5c244881002309df84d20290ddf3f8589"
                    "67ed010202202a479b3da5080ea475d310ff13494654b42db75886a8808bd211b4"
                    "bdb9146a7a"
                ),
                "signSignature": (
                    "3045022100e1dcab3406bbeb968146a4a391909ce41df9b71592a753b001e7c2ee"
                    "1d382c5102202a74aeafd4a152ec61854636fbae829c41f1416c1e0637a0809408"
                    "394973099f"
                ),
                "id": (
                    "1e255f07dc25ce22d900ea81663c8f00d05a7b7c061e6fc3c731b05d642fa0b9"
                ),
                "senderId": "DB8LnnQqYvHpG4WkGJ9AJWBYEct7G3yRZg",
                "hop": 2,
                "broadcast": False,
                "blockId": "7176646138626297930",
            },
            {
                "type": 0,
                "amount": 555750,
                "fee": 10000000,
                "recipientId": "D7pcLJNGe197ibmWEmT8mM9KKU1htrcDyW",
                "timestamp": 24760417,
                "asset": {},
                "vendorField": "Goose Voter - True Block Weight",
                "senderPublicKey": (
                    "0265c1f6b8c1966a90f3fed7bc32fd4f42238ab4938fdb2a4e7ddd01ae8b58b4c0"
                ),
                "signature": (
                    "3045022100cd4fa9855227be11e17201419dacfbbd5d9946df8d6792a948816002"
                    "5693821402207fb83969bad6a26959f437b5bb88e255b0a48eb04964d0c0d29f7e"
                    "e94bd15e11"
                ),
                "signSignature": (
                    "304402205f50c2991a17743d17ffbb09159cadc35a3f848044261842879ccf5be9"
                    "d81c5e022023bf21c32fb6e94494104f15f8d3a942ab120d0abd6fb4c93790b68e"
                    "1b307a79"
                ),
                "id": (
                    "66336c61d6ec623f8a1d2fd156a0fac16a4fe93bb3fba337859355c2119923a8"
                ),
                "senderId": "DB8LnnQqYvHpG4WkGJ9AJWBYEct7G3yRZg",
                "hop": 2,
                "broadcast": False,
                "blockId": "7176646138626297930",
            },
            {
                "type": 0,
                "amount": 555760,
                "fee": 10000000,
                "recipientId": "DD4yhwzryQdNGqKtezmycToQv63g27Tqqq",
                "timestamp": 24760418,
                "asset": {},
                "vendorField": "Goose Voter - True Block Weight",
                "senderPublicKey": (
                    "0265c1f6b8c1966a90f3fed7bc32fd4f42238ab4938fdb2a4e7ddd01ae8b58b4c0"
                ),
                "signature": (
                    "30450221009c792062e13399ac6756b2e9f137194d06e106360ac0f3e24e55c724"
                    "9cee0b3602205dc1d9c76d0451d1cb5a2396783a13e6d2d790ccfd49291e3d0a78"
                    "349f7ea0e8"
                ),
                "signSignature": (
                    "30440220083ba8a9af49b8be6e93794d71ec43ffc96a158375810e5d9f2478e716"
                    "55315b0220278402ecaa1d224dab9f0f3b28295bbaea339c85c7400edafdc49df8"
                    "7439fc64"
                ),
                "id": (
                    "78db36f7d79f51c67d7210ee3819dfb8d0d47b16a7484ebf55c5a055b17209a3"
                ),
                "senderId": "DB8LnnQqYvHpG4WkGJ9AJWBYEct7G3yRZg",
                "hop": 2,
                "broadcast": False,
                "blockId": "7176646138626297930",
            },
            {
                "type": 0,
                "amount": 555760,
                "fee": 10000000,
                "recipientId": "D5LiYGXL5keycWuTF6AFFwSRc6Mt4uEHMu",
                "timestamp": 24760419,
                "asset": {},
                "vendorField": "Goose Voter - True Block Weight",
                "senderPublicKey": (
                    "0265c1f6b8c1966a90f3fed7bc32fd4f42238ab4938fdb2a4e7ddd01ae8b58b4c0"
                ),
                "signature": (
                    "3044022063c65263e42be02bd9831b375c1d76a88332f00ed0557ecc1e7d2375ca"
                    "40070902206797b5932c0bad68444beb5a38daa7cadf536ee2144e0d9777b81228"
                    "4d14374e"
                ),
                "signSignature": (
                    "3045022100b04da6692f75d43229ffd8486c1517e8952d38b4c03dfac38b6b3601"
                    "90a5c33e0220776622e5f09f92a1258b4a011f22181c977b622b8d1bbb2f83b42f"
                    "4126d00739"
                ),
                "id": (
                    "83c80bb58777bb43f5037544b44ef69f191d3548fd1b2a00bed368f9f0d694c5"
                ),
                "senderId": "DB8LnnQqYvHpG4WkGJ9AJWBYEct7G3yRZg",
                "hop": 2,
                "broadcast": False,
                "blockId": "7176646138626297930",
            },
            {
                "type": 0,
                "amount": 555750,
                "fee": 10000000,
                "recipientId": "DPopNLwMvv4zSjdZnqUk8HFH13Mcb7NbEK",
                "timestamp": 24760416,
                "asset": {},
                "vendorField": "Goose Voter - True Block Weight",
                "senderPublicKey": (
                    "0265c1f6b8c1966a90f3fed7bc32fd4f42238ab4938fdb2a4e7ddd01ae8b58b4c0"
                ),
                "signature": (
                    "3045022100d4513c3608c2072e38e7a0e3bb8daf2cd5f7cc6fec9a5570dccd1eda"
                    "696c591902202ecbbf3c9d0757be7b23c8b1cc6481c51600d158756c47fcb6f4a7"
                    "f4893e31c4"
                ),
                "signSignature": (
                    "304402201fed4858d0806dd32220960900a871dd2f60e1f623af75feef9b1034a9"
                    "a0a46402205a29b27c63fcc3e1ee1e77ecbbf4dd6e7db09901e7a09b9fd490cd68"
                    "d62392cb"
                ),
                "id": (
                    "d2faf992fdd5da96d6d15038b6ddb65230338fa2096e45e44da51daad5e2f3ca"
                ),
                "senderId": "DB8LnnQqYvHpG4WkGJ9AJWBYEct7G3yRZg",
                "hop": 2,
                "broadcast": False,
                "blockId": "7176646138626297930",
            },
        ],
    }


@pytest.fixture
def crypto_transaction():
    transaction = Transaction()
    transaction.version = 1
    transaction.network = 30
    transaction.type = 0
    transaction.timestamp = 24760418
    transaction.sender_public_key = (
        "0265c1f6b8c1966a90f3fed7bc32fd4f42238ab4938fdb2a4e7ddd01ae8b58b4c0"
    )
    transaction.fee = 10000000
    transaction.amount = 555760
    transaction.expiration = 0
    transaction.recipient_id = "DB4gFuDztmdGALMb8i1U4Z4R5SktxpNTAY"
    transaction.asset = {}
    transaction.vendor_field = "Goose Voter - True Block Weight"
    transaction.vendor_field_hex = (
        b"476f6f736520566f746572202d205472756520426c6f636b20576569676874"
    )
    transaction.id = "170543154a3b79459cbaa529f9f62b6f1342682799eb549dbf09fcca2d1f9c11"
    transaction.signature = (
        "304402204f12469157b19edd06ba25fcad3d4a5ef5b057c23f9e02de4641e6f8eef0553e022010"
        "121ab282f83efe1043de9c16bbf2c6845a03684229a0d7c965ffb9abdfb978"
    )
    transaction.second_signature = (
        "30450221008327862f0b9178d6665f7d6674978c5caf749649558d814244b1c66cdf945c400220"
        "15918134ef01fed3fe2a2efde3327917731344332724522c75c2799a14f78717"
    )
    transaction.sign_signature = (
        "30450221008327862f0b9178d6665f7d6674978c5caf749649558d814244b1c66cdf945c400220"
        "15918134ef01fed3fe2a2efde3327917731344332724522c75c2799a14f78717"
    )
    transaction.signatures = []
    transaction.block_id = "7176646138626297930"
    transaction.sequence = 0
    transaction.timelock = None
    transaction.timelock_type = None
    transaction.ipfs_hash = None
    transaction.payments = None
    return transaction


@pytest.fixture
def crypto_block(crypto_transaction):
    block = Block()
    block.height = 2243161
    block.id = "7176646138626297930"
    block.id_hex = b"639891a3bb7fd04a"
    block.number_of_transactions = 7
    block.payload_hash = (
        "3784b953afcf936bdffd43fdf005b5732b49c1fc6b11e195c364c20b2eb06282"
    )
    block.payload_length = 224
    block.previous_block = "3112633353705641986"
    block.previous_block_hex = b"2b324b8b33a85802"
    block.reward = 200000000
    block.timestamp = 24760440
    block.total_amount = 3890300
    block.total_fee = 70000000
    block.version = 0
    block.generator_public_key = (
        "020f5df4d2bc736d12ce43af5b1663885a893fade7ee5e62b3cc59315a63e6a325"
    )
    block.block_signature = (
        "3045022100eee6c37b5e592e99811d588532726353592923f347c701d52912e6d583443e40022"
        "0277ffe38ad31e216ba0907c4738fed19b2071246b150c72c0a52bae4477ebe29"
    )

    block.transactions.append(crypto_transaction)

    transaction2 = Transaction()
    transaction2.version = 1
    transaction2.network = 30
    transaction2.type = 0
    transaction2.timestamp = 24760416
    transaction2.sender_public_key = (
        "0265c1f6b8c1966a90f3fed7bc32fd4f42238ab4938fdb2a4e7ddd01ae8b58b4c0"
    )
    transaction2.fee = 10000000
    transaction2.amount = 555750
    transaction2.expiration = 0
    transaction2.recipient_id = "DGExsNogZR7JFa2656ZFP9TMWJYJh5djzQ"
    transaction2.asset = {}
    transaction2.vendor_field = "Goose Voter - True Block Weight"
    transaction2.vendor_field_hex = (
        b"476f6f736520566f746572202d205472756520426c6f636b20576569676874"
    )
    transaction2.id = "1da153f37eceda233ff1b407ac18e47b3cae47c14cdcd5297d929618a916c4a7"
    transaction2.signature = (
        "304402205f82feb8c5d1d79c565c2ff7badb93e4c9827b132d135dda11cb25427d4ef8ac02205f"
        "f136f970533c4ec4c7d0cd1ea7e02d7b62629b66c6c93265f608d7f2389727"
    )
    transaction2.second_signature = (
        "304402207e912031fcc700d8a55fbc415993302a0d8e6aea128397141b640b6dba52331702201f"
        "d1ad3984e42af44f548907add6cb7ad72ca0070c8cc1d8dc9bbda208c56bd9"
    )
    transaction2.sign_signature = (
        "304402207e912031fcc700d8a55fbc415993302a0d8e6aea128397141b640b6dba52331702201f"
        "d1ad3984e42af44f548907add6cb7ad72ca0070c8cc1d8dc9bbda208c56bd9"
    )
    transaction2.signatures = []
    transaction2.block_id = "7176646138626297930"
    transaction2.sequence = 1
    transaction2.timelock = None
    transaction2.timelock_type = None
    transaction2.ipfs_hash = None
    transaction2.payments = None
    block.transactions.append(transaction2)

    transaction3 = Transaction()
    transaction3.version = 1
    transaction3.network = 30
    transaction3.type = 0
    transaction3.timestamp = 24760420
    transaction3.sender_public_key = (
        "0265c1f6b8c1966a90f3fed7bc32fd4f42238ab4938fdb2a4e7ddd01ae8b58b4c0"
    )
    transaction3.fee = 10000000
    transaction3.amount = 555770
    transaction3.expiration = 0
    transaction3.recipient_id = "DHGK5np6LuMMErfRfC5CmjpGu3ME85c25n"
    transaction3.asset = {}
    transaction3.vendor_field = "Goose Voter - True Block Weight"
    transaction3.vendor_field_hex = (
        b"476f6f736520566f746572202d205472756520426c6f636b20576569676874"
    )
    transaction3.id = "1e255f07dc25ce22d900ea81663c8f00d05a7b7c061e6fc3c731b05d642fa0b9"
    transaction3.signature = (
        "304502210083216e6969e068770e6d2fe5c244881002309df84d20290ddf3f858967ed01020220"
        "2a479b3da5080ea475d310ff13494654b42db75886a8808bd211b4bdb9146a7a"
    )
    transaction3.second_signature = (
        "3045022100e1dcab3406bbeb968146a4a391909ce41df9b71592a753b001e7c2ee1d382c510220"
        "2a74aeafd4a152ec61854636fbae829c41f1416c1e0637a0809408394973099f"
    )
    transaction3.sign_signature = (
        "3045022100e1dcab3406bbeb968146a4a391909ce41df9b71592a753b001e7c2ee1d382c510220"
        "2a74aeafd4a152ec61854636fbae829c41f1416c1e0637a0809408394973099f"
    )
    transaction3.signatures = []
    transaction3.block_id = "7176646138626297930"
    transaction3.sequence = 2
    transaction3.timelock = None
    transaction3.timelock_type = None
    transaction3.ipfs_hash = None
    transaction3.payments = None
    block.transactions.append(transaction3)

    transaction4 = Transaction()
    transaction4.version = 1
    transaction4.network = 30
    transaction4.type = 0
    transaction4.timestamp = 24760417
    transaction4.sender_public_key = (
        "0265c1f6b8c1966a90f3fed7bc32fd4f42238ab4938fdb2a4e7ddd01ae8b58b4c0"
    )
    transaction4.fee = 10000000
    transaction4.amount = 555750
    transaction4.expiration = 0
    transaction4.recipient_id = "D7pcLJNGe197ibmWEmT8mM9KKU1htrcDyW"
    transaction4.asset = {}
    transaction4.vendor_field = "Goose Voter - True Block Weight"
    transaction4.vendor_field_hex = (
        b"476f6f736520566f746572202d205472756520426c6f636b20576569676874"
    )
    transaction4.id = "66336c61d6ec623f8a1d2fd156a0fac16a4fe93bb3fba337859355c2119923a8"
    transaction4.signature = (
        "3045022100cd4fa9855227be11e17201419dacfbbd5d9946df8d6792a948816002569382140220"
        "7fb83969bad6a26959f437b5bb88e255b0a48eb04964d0c0d29f7ee94bd15e11"
    )
    transaction4.second_signature = (
        "304402205f50c2991a17743d17ffbb09159cadc35a3f848044261842879ccf5be9d81c5e022023"
        "bf21c32fb6e94494104f15f8d3a942ab120d0abd6fb4c93790b68e1b307a79"
    )
    transaction4.sign_signature = (
        "304402205f50c2991a17743d17ffbb09159cadc35a3f848044261842879ccf5be9d81c5e022023"
        "bf21c32fb6e94494104f15f8d3a942ab120d0abd6fb4c93790b68e1b307a79"
    )
    transaction4.signatures = []
    transaction4.block_id = "7176646138626297930"
    transaction4.sequence = 3
    transaction4.timelock = None
    transaction4.timelock_type = None
    transaction4.ipfs_hash = None
    transaction4.payments = None
    block.transactions.append(transaction4)

    transaction5 = Transaction()
    transaction5.version = 1
    transaction5.network = 30
    transaction5.type = 0
    transaction5.timestamp = 24760418
    transaction5.sender_public_key = (
        "0265c1f6b8c1966a90f3fed7bc32fd4f42238ab4938fdb2a4e7ddd01ae8b58b4c0"
    )
    transaction5.fee = 10000000
    transaction5.amount = 555760
    transaction5.expiration = 0
    transaction5.recipient_id = "DD4yhwzryQdNGqKtezmycToQv63g27Tqqq"
    transaction5.asset = {}
    transaction5.vendor_field = "Goose Voter - True Block Weight"
    transaction5.vendor_field_hex = (
        b"476f6f736520566f746572202d205472756520426c6f636b20576569676874"
    )
    transaction5.id = "78db36f7d79f51c67d7210ee3819dfb8d0d47b16a7484ebf55c5a055b17209a3"
    transaction5.signature = (
        "30450221009c792062e13399ac6756b2e9f137194d06e106360ac0f3e24e55c7249cee0b360220"
        "5dc1d9c76d0451d1cb5a2396783a13e6d2d790ccfd49291e3d0a78349f7ea0e8"
    )
    transaction5.second_signature = (
        "30440220083ba8a9af49b8be6e93794d71ec43ffc96a158375810e5d9f2478e71655315b022027"
        "8402ecaa1d224dab9f0f3b28295bbaea339c85c7400edafdc49df87439fc64"
    )
    transaction5.sign_signature = (
        "30440220083ba8a9af49b8be6e93794d71ec43ffc96a158375810e5d9f2478e71655315b022027"
        "8402ecaa1d224dab9f0f3b28295bbaea339c85c7400edafdc49df87439fc64"
    )
    transaction5.signatures = []
    transaction5.block_id = "7176646138626297930"
    transaction5.sequence = 4
    transaction5.timelock = None
    transaction5.timelock_type = None
    transaction5.ipfs_hash = None
    transaction5.payments = None
    block.transactions.append(transaction5)

    transaction6 = Transaction()
    transaction6.version = 1
    transaction6.network = 30
    transaction6.type = 0
    transaction6.timestamp = 24760419
    transaction6.sender_public_key = (
        "0265c1f6b8c1966a90f3fed7bc32fd4f42238ab4938fdb2a4e7ddd01ae8b58b4c0"
    )
    transaction6.fee = 10000000
    transaction6.amount = 555760
    transaction6.expiration = 0
    transaction6.recipient_id = "D5LiYGXL5keycWuTF6AFFwSRc6Mt4uEHMu"
    transaction6.asset = {}
    transaction6.vendor_field = "Goose Voter - True Block Weight"
    transaction6.vendor_field_hex = (
        b"476f6f736520566f746572202d205472756520426c6f636b20576569676874"
    )
    transaction6.id = "83c80bb58777bb43f5037544b44ef69f191d3548fd1b2a00bed368f9f0d694c5"
    transaction6.signature = (
        "3044022063c65263e42be02bd9831b375c1d76a88332f00ed0557ecc1e7d2375ca400709022067"
        "97b5932c0bad68444beb5a38daa7cadf536ee2144e0d9777b812284d14374e"
    )
    transaction6.second_signature = (
        "3045022100b04da6692f75d43229ffd8486c1517e8952d38b4c03dfac38b6b360190a5c33e0220"
        "776622e5f09f92a1258b4a011f22181c977b622b8d1bbb2f83b42f4126d00739"
    )
    transaction6.sign_signature = (
        "3045022100b04da6692f75d43229ffd8486c1517e8952d38b4c03dfac38b6b360190a5c33e0220"
        "776622e5f09f92a1258b4a011f22181c977b622b8d1bbb2f83b42f4126d00739"
    )
    transaction6.signatures = []
    transaction6.block_id = "7176646138626297930"
    transaction6.sequence = 5
    transaction6.timelock = None
    transaction6.timelock_type = None
    transaction6.ipfs_hash = None
    transaction6.payments = None
    block.transactions.append(transaction6)

    transaction7 = Transaction()
    transaction7.version = 1
    transaction7.network = 30
    transaction7.type = 0
    transaction7.timestamp = 24760416
    transaction7.sender_public_key = (
        "0265c1f6b8c1966a90f3fed7bc32fd4f42238ab4938fdb2a4e7ddd01ae8b58b4c0"
    )
    transaction7.fee = 10000000
    transaction7.amount = 555750
    transaction7.expiration = 0
    transaction7.recipient_id = "DPopNLwMvv4zSjdZnqUk8HFH13Mcb7NbEK"
    transaction7.asset = {}
    transaction7.vendor_field = "Goose Voter - True Block Weight"
    transaction7.vendor_field_hex = (
        b"476f6f736520566f746572202d205472756520426c6f636b20576569676874"
    )
    transaction7.id = "d2faf992fdd5da96d6d15038b6ddb65230338fa2096e45e44da51daad5e2f3ca"
    transaction7.signature = (
        "3045022100d4513c3608c2072e38e7a0e3bb8daf2cd5f7cc6fec9a5570dccd1eda696c59190220"
        "2ecbbf3c9d0757be7b23c8b1cc6481c51600d158756c47fcb6f4a7f4893e31c4"
    )
    transaction7.second_signature = (
        "304402201fed4858d0806dd32220960900a871dd2f60e1f623af75feef9b1034a9a0a46402205a"
        "29b27c63fcc3e1ee1e77ecbbf4dd6e7db09901e7a09b9fd490cd68d62392cb"
    )
    transaction7.sign_signature = (
        "304402201fed4858d0806dd32220960900a871dd2f60e1f623af75feef9b1034a9a0a46402205a"
        "29b27c63fcc3e1ee1e77ecbbf4dd6e7db09901e7a09b9fd490cd68d62392cb"
    )
    transaction7.signatures = []
    transaction7.block_id = "7176646138626297930"
    transaction7.sequence = 6
    transaction7.timelock = None
    transaction7.timelock_type = None
    transaction7.ipfs_hash = None
    transaction7.payments = None
    block.transactions.append(transaction7)
    return block
