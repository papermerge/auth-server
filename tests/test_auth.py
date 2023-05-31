from auth_server.auth import verify_password


def test_verify_password():
    password = "123"
    hashed_password = "abc"
    assert verify_password(password, hashed_password)
