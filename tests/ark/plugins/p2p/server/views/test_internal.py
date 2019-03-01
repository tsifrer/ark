


def test_bla(p2p_app):

    print(p2p_app)

    response = p2p_app.get('/')

    print(response.json['foo'])