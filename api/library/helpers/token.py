"""Token helpers."""

import typing

import jwt


def decode(token: str) -> typing.Dict[str, typing.Any]:
    """
    Decode a token.

    Assume the token has already been verified elsewhere.

    Args:
        token: The token to decode.

    Returns:
        The decoded token.

    """
    # Assume that the token has already been verified
    return jwt.decode(token, algorithms="RS256", options={"verify_signature": False})
