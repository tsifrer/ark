import pytest
from webtest import TestApp
from pyramid import testing

from tests.ark.fixtures import *

from ark.plugins.p2p.server import create_app


@pytest.fixture(scope='session')
def p2p_app():
    app = create_app()
    return TestApp(app)
