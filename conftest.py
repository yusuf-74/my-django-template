import pytest
from rest_framework.test import APIClient


@pytest.fixture
def authenticated_user(user):
    client = APIClient.force_authenticate(user=user)
    return client


@pytest.fixture
def unauthenticated_user():
    return APIClient()
