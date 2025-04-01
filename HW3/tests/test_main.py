from fastapi_cache import FastAPICache


async def test_unauthenticated_route(client):
    response= await client.get("/unauthenticated-route")
    assert response.status_code == 200, response.text
    assert response.json()['message'] == "Hello human!"


async def test_authenticated_route(client):
    response= await client.get("/authenticated-route")
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Unauthorized"


async def test_registration(client, registred_user):
    response = await client.post( "http://127.0.0.1:8000/auth/register", json=registred_user)
    assert response.status_code == 201, response.text
    assert response.json()["email"] == "test12@mail.ru"
    assert response.json()["name"] == "Test12"


async def test_login(client, authorized_user, registred_user):
    await client.post("http://127.0.0.1:8000/auth/register", json=registred_user)
    response = await client.post( "http://127.0.0.1:8000/auth/jwt/login",
                              data=authorized_user)
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    assert token is not None
    assert response.json()["token_type"] == "bearer"


async def test_bad_credentials(client, registred_user, fake_user):
    await client.post("http://127.0.0.1:8000/auth/register", json=registred_user)
    response = await client.post("http://127.0.0.1:8000/auth/jwt/login",
                                 data=fake_user)
    assert response.status_code == 400, response.text
    assert response.json()["detail"] == "LOGIN_BAD_CREDENTIALS", response.text


async def test_authorization(client, registred_user, authorized_user):
    await client.post("http://127.0.0.1:8000/auth/register", json=registred_user)
    token = await client.post("http://127.0.0.1:8000/auth/jwt/login", data=authorized_user)
    token=token.json()["access_token"]
    response = await client.get("/authenticated-route", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Hello test12@mail.ru!", response.text


async def test_shorten(client, registred_user, authorized_user):
    await client.post("http://127.0.0.1:8000/auth/register", json=registred_user)
    token = await client.post("http://127.0.0.1:8000/auth/jwt/login", data=authorized_user)
    token = token.json()["access_token"]
    long_link="https%3A%2F%2Fyandex.ru%2Fvideo%2Fpreview%2F4439900293420889775"
    response = await client.post(f"http://127.0.0.1:8000/links/shorten?link={long_link}", headers={"Authorization": f"Bearer {token}"})
    assert response.json()["status"] == "success", response.text
    assert len(response.json()["data"]) == 6, response.text
#

async def test_redirect(client, registred_user, authorized_user):
    await client.post("http://127.0.0.1:8000/auth/register", json=registred_user)
    token = await client.post("http://127.0.0.1:8000/auth/jwt/login", data=authorized_user)
    token = token.json()["access_token"]
    long_link="https%3A%2F%2Fyandex.ru%2Fvideo%2Fpreview%2F4439900293420889775"
    short_link = await client.post(f"http://127.0.0.1:8000/links/shorten?link={long_link}", headers={"Authorization": f"Bearer {token}"})
    short_link=short_link.json()["data"]
    FastAPICache.init(backend="simple")
    response= await client.get (f"http://127.0.0.1:8000/links/{short_link}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 307, response.text
#
#
# # async def test_update_short_link(client):
#     response = await client.put (f"http://127.0.0.1:8000/links/{short_link}?long_link={long_link}")
#     mock.return_value = {"message": "New short-link yyyyyy for https://yandex.ru/video/preview/4439900293420889775"}
#     assert response.json() == {"message": "New short-link yyyyyy for https://yandex.ru/video/preview/4439900293420889775"}
#

#RUN IN CML:
# pytest tests/test_main.py -v

#покрытие тестами
#coverage run -m pytest tests/test_main.py
#coverage report
#coverage html

