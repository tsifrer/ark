


def test_order():
    data = [
        {'public_key': 'g', 'balance': 5000},
        {'public_key': 'b', 'balance': 4000},
        {'public_key': 'c', 'balance': 2000},
        {'public_key': 'd', 'balance': 3000},
        {'public_key': 'e', 'balance': 6000},
        {'public_key': 'f', 'balance': 1000},
        {'public_key': 'a', 'balance': 5000},
    ]

    data.sort(key=lambda x: (-x['balance'], x['public_key']))

    print(data)
