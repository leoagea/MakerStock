import pytest


@pytest.mark.django_db
def test_anonymous_request_to_home_redirects_to_login(anonymous_client):
    response = anonymous_client.get("/")
    assert response.status_code == 302
    assert response.url == "/accounts/login/?next=/"


@pytest.mark.django_db
def test_anonymous_request_to_components_redirects_to_login(anonymous_client):
    response = anonymous_client.get("/components/")
    assert response.status_code == 302
    assert response.url.startswith("/accounts/login/")


@pytest.mark.django_db
def test_login_page_itself_is_reachable_while_anonymous(anonymous_client):
    response = anonymous_client.get("/accounts/login/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_login_is_reachable_while_anonymous(anonymous_client):
    response = anonymous_client.get("/admin/login/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_authenticated_client_can_reach_home(client):
    response = client.get("/")
    assert response.status_code == 200
