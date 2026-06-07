from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_is_not_plain_text(self):
        hashed = hash_password("mysecret")
        assert hashed != "mysecret"

    def test_correct_password_verifies(self):
        hashed = hash_password("mysecret")
        assert verify_password("mysecret", hashed) is True

    def test_wrong_password_fails(self):
        hashed = hash_password("mysecret")
        assert verify_password("wrongpassword", hashed) is False

    def test_same_password_different_hashes(self):
        h1 = hash_password("mysecret")
        h2 = hash_password("mysecret")
        assert h1 != h2  # bcrypt salting


class TestJWT:
    def test_token_encodes_and_decodes(self):
        token = create_access_token({"sub": "42"})
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "42"

    def test_invalid_token_returns_none(self):
        assert decode_access_token("not.a.real.token") is None

    def test_tampered_token_returns_none(self):
        token = create_access_token({"sub": "42"})
        tampered = token[:-5] + "XXXXX"
        assert decode_access_token(tampered) is None

    def test_expired_token_returns_none(self):
        from datetime import timedelta
        token = create_access_token({"sub": "42"}, expires_delta=timedelta(seconds=-1))
        assert decode_access_token(token) is None