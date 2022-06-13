from unittest import mock

import pytest
from environs import Env
from fakeredis import FakeRedis

env = Env()


@pytest.fixture
def fake_redis():
    with (
        mock.patch(
            "wikicrawl.stub.redis.Redis", return_value=FakeRedis(connection_pool=None, charset=None, errors=None)
        ),
    ):
        yield
