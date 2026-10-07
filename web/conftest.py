import pytest
from django.test import Client


@pytest.fixture
def client(client, django_user_model):
    """Every test's `client` is logged in by default, since the whole app
    sits behind LoginRequiredMiddleware. Use `anonymous_client` for tests
    that specifically need to exercise the logged-out path.
    """
    user = django_user_model.objects.create_user(username="testuser", password="testpass123")
    client.force_login(user)
    return client


@pytest.fixture
def anonymous_client():
    return Client()
