"""Tests for package security."""

from open_alchemy import package_security


def test_create():
    """
    GIVEN sub
    WHEN create is called
    THEN credentials are returned with minimum lengths and no obvious relationships.
    """
    sub = "sub 1"

    returned_credentials = package_security.create(sub=sub)

    assert returned_credentials.public_key is not None
    assert returned_credentials.public_key.startswith("pk_")
    assert sub not in returned_credentials.public_key
    assert len(returned_credentials.public_key) >= 32

    assert returned_credentials.secret_key is not None
    assert returned_credentials.secret_key.startswith("sk_")
    assert returned_credentials.secret_key not in returned_credentials.public_key
    assert returned_credentials.public_key not in returned_credentials.secret_key
    assert len(returned_credentials.secret_key) >= 32

    assert returned_credentials.secret_key_hash is not None
    assert (
        returned_credentials.secret_key.encode()
        not in returned_credentials.secret_key_hash
    )
    assert (
        returned_credentials.secret_key_hash
        not in returned_credentials.secret_key.encode()
    )
    assert (
        returned_credentials.public_key.encode()
        not in returned_credentials.secret_key_hash
    )
    assert (
        returned_credentials.secret_key_hash
        not in returned_credentials.public_key.encode()
    )
    assert len(returned_credentials.secret_key_hash) >= 32

    assert returned_credentials.salt is not None
    assert returned_credentials.secret_key.encode() not in returned_credentials.salt
    assert returned_credentials.salt not in returned_credentials.secret_key.encode()
    assert returned_credentials.public_key.encode() not in returned_credentials.salt
    assert returned_credentials.salt not in returned_credentials.public_key.encode()
    assert returned_credentials.secret_key_hash not in returned_credentials.salt
    assert returned_credentials.salt not in returned_credentials.secret_key_hash
    assert len(returned_credentials.salt) >= 32


def test_retrieve():
    """
    GIVEN credentials
    WHEN retrieve is called with the sub and salt from the credentials
    THEN the returned secret is equal to the secret of the credentials.
    """
    sub = "sub 1"
    credentials = package_security.create(sub=sub)

    returned_secret_key = package_security.retrieve(sub=sub, salt=credentials.salt)

    assert returned_secret_key == credentials.secret_key
