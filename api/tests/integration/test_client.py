"""Tests for spec controller."""


import pytest
from library import config
from library.facades import storage

OPTIONS_TESTS = [
    pytest.param("/v1/specs/spec1", "PUT", id="/v1/specs/{spec-id}"),
]


@pytest.mark.parametrize("path, method", OPTIONS_TESTS)
def test_endpoint_options(client, path, method):
    """
    GIVEN path and method
    WHEN OPTIONS {path} is called with the CORS Method and X-LANGUAGE Headers
    THEN Access-Control-Allow-Headers is returned with x-language.
    """
    respose = client.options(
        path,
        headers={
            "Access-Control-Request-Method": method,
            "Access-Control-Request-Headers": "x-language",
        },
    )

    assert "Access-Control-Allow-Headers" in respose.headers
    assert (
        respose.headers["Access-Control-Allow-Headers"]
        == config.get_env().access_control_allow_headers
    )


def test_specs_put_unauthorized(client):
    """
    GIVEN spec id and data
    WHEN PUT /v1/specs/{spec-id} is called without the Authorization header
    THEN 401 is returned.
    """
    data = "spec 1"
    spec_id = "id 1"

    respose = client.put(f"/v1/specs/{spec_id}", data=data)

    assert respose.status_code == 401


def test_specs_put(client):
    """
    GIVEN spec id and data
    WHEN PUT /v1/specs/{spec-id} is called with the Authorization header
    THEN the value is stored against the spec id.
    """
    data = "spec 1"
    spec_id = "id 1"

    respose = client.put(
        f"/v1/specs/{spec_id}", data=data, headers={"Authorization": "Bearer token 1"}
    )

    assert respose.status_code == 204
    assert "Access-Control-Allow-Origin" in respose.headers
    assert (
        respose.headers["Access-Control-Allow-Origin"]
        == config.get_env().access_control_allow_origin
    )

    assert storage.get_storage().get(key=f"{spec_id}/spec.json") == data
