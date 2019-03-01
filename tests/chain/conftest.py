import pytest
from webtest import TestApp

from tests.chain.fixtures import *

from chain.p2p_service.server import create_app


@pytest.fixture(scope='session')
def p2p_service():
    app = create_app()
    return TestApp(app)
