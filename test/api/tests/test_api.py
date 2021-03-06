"""Tests for the API."""
# pylint: disable=too-many-statements

import json
from urllib import error, request

import pytest


@pytest.mark.parametrize(
    "test_request",
    [
        request.Request(
            "https://package.api.openalchemy.io/v1/specs",
            method="GET",
        ),
        request.Request(
            "https://package.api.openalchemy.io/v1/specs/spec1",
            method="GET",
        ),
        request.Request(
            "https://package.api.openalchemy.io/v1/specs/spec1",
            method="DELETE",
        ),
        request.Request(
            "https://package.api.openalchemy.io/v1/specs/spec1",
            data=b"data 1",
            method="PUT",
        ),
        request.Request(
            "https://package.api.openalchemy.io/v1/specs/spec1/versions",
            method="GET",
        ),
        request.Request(
            "https://package.api.openalchemy.io/v1/specs/spec1/versions/1",
            method="GET",
        ),
        request.Request(
            "https://package.api.openalchemy.io/v1/specs/spec1/versions/1",
            data=b"data 1",
            method="PUT",
        ),
        request.Request(
            "https://package.api.openalchemy.io/v1/credentials/default",
            method="GET",
        ),
        request.Request(
            "https://package.api.openalchemy.io/v1/credentials/default",
            method="DELETE",
        ),
    ],
)
def test_unauthorized(test_request):
    """
    GIVEN request
    WHEN the request is executed
    THEN 401 is returned.
    """
    with pytest.raises(error.HTTPError) as exc:
        request.urlopen(test_request)
    assert exc.value.code == 401

    test_request.headers["Authorization"] = "Bearer invalid"
    with pytest.raises(error.HTTPError) as exc:
        request.urlopen(test_request)
    assert exc.value.code == 401


def test_specs_create_get_delete(access_token, spec_name):
    """
    GIVEN spec
    WHEN it is created, retrieved and deleted
    THEN no errors are returned.
    """
    # Initial list of specs, expect it to be empty
    test_request = request.Request(
        "https://package.api.openalchemy.io/v1/specs",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    with request.urlopen(test_request) as response:
        assert response.status == 200
        assert json.loads(response.read().decode()) == []

    # Try to upload a spec that is invalid
    test_request = request.Request(
        "https://package.api.openalchemy.io/v1/specs/spec1",
        data=b"invalid spec",
        headers={"Authorization": f"Bearer {access_token}", "X-LANGUAGE": "JSON"},
        method="PUT",
    )

    with pytest.raises(error.HTTPError) as exc:
        request.urlopen(test_request)
    assert exc.value.code == 400

    # Upload a spec that is valid
    version = "1"
    title = "title 1"
    description = "description 1"
    spec = {
        "info": {
            "title": title,
            "description": description,
            "version": version,
        },
        "components": {
            "schemas": {
                "Schema": {
                    "type": "object",
                    "x-tablename": "schema",
                    "properties": {"id": {"type": "integer"}},
                }
            }
        },
    }
    spec_str = json.dumps(spec)
    test_request = request.Request(
        f"https://package.api.openalchemy.io/v1/specs/{spec_name}",
        data=spec_str.encode(),
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-LANGUAGE": "JSON",
            "Content-Type": "text/plain",
        },
        method="PUT",
    )

    with request.urlopen(test_request) as response:
        assert response.status == 204

    # Check that the spec is now listed
    test_request = request.Request(
        "https://package.api.openalchemy.io/v1/specs",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    with request.urlopen(test_request) as response:
        assert response.status == 200
        returned_specs = json.loads(response.read().decode())
        assert len(returned_specs) == 1
        returned_spec = returned_specs[0]
        assert returned_spec["name"] == spec_name
        assert returned_spec["id"] == spec_name.lower()
        assert returned_spec["version"] == version
        assert returned_spec["title"] == title
        assert returned_spec["description"] == description
        assert "updated_at" in returned_spec

    # Check that the spec can be retrieved
    test_request = request.Request(
        f"https://package.api.openalchemy.io/v1/specs/{spec_name}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    with request.urlopen(test_request) as response:
        assert response.status == 200
        response_json = json.loads(response.read().decode())
        spec_str = response_json["value"]
        assert "Schema:" in spec_str
        assert "x-tablename:" in spec_str
        assert ": schema" in spec_str
        assert response_json["name"] == spec_name
        assert response_json["id"] == spec_name.lower()
        assert response_json["version"] == version
        assert response_json["title"] == title
        assert response_json["description"] == description
        assert "updated_at" in response_json

    # Delete the spec
    test_request = request.Request(
        f"https://package.api.openalchemy.io/v1/specs/{spec_name}",
        headers={"Authorization": f"Bearer {access_token}"},
        method="DELETE",
    )

    with request.urlopen(test_request) as response:
        assert response.status == 204

    # Check that the spec can no longer be retrieved
    test_request = request.Request(
        f"https://package.api.openalchemy.io/v1/specs/{spec_name}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    with pytest.raises(error.HTTPError) as exc:
        request.urlopen(test_request)
    assert exc.value.code == 404

    # Check that the spec is no longer listed
    test_request = request.Request(
        "https://package.api.openalchemy.io/v1/specs",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    with request.urlopen(test_request) as response:
        assert response.status == 200
        assert json.loads(response.read().decode()) == []


def test_specs_versions_create_get_delete(access_token, spec_name):
    """
    GIVEN spec
    WHEN it is created, retrieved and deleted for a specific version
    THEN no errors are returned.
    """
    # Initial list of specs, expect it to be empty
    test_request = request.Request(
        "https://package.api.openalchemy.io/v1/specs",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    with request.urlopen(test_request) as response:
        assert response.status == 200
        assert json.loads(response.read().decode()) == []

    # Try to upload a spec that is invalid
    version = "1"
    test_request = request.Request(
        f"https://package.api.openalchemy.io/v1/specs/spec1/versions/{version}",
        data=b"invalid spec",
        headers={"Authorization": f"Bearer {access_token}", "X-LANGUAGE": "JSON"},
        method="PUT",
    )

    with pytest.raises(error.HTTPError) as exc:
        request.urlopen(test_request)
    assert exc.value.code == 400

    # Upload a spec that is valid
    spec = {
        "info": {"version": version},
        "components": {
            "schemas": {
                "Schema": {
                    "type": "object",
                    "x-tablename": "schema",
                    "properties": {"id": {"type": "integer"}},
                }
            }
        },
    }
    spec_str = json.dumps(spec)
    test_request = request.Request(
        f"https://package.api.openalchemy.io/v1/specs/{spec_name}/versions/{version}",
        data=spec_str.encode(),
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-LANGUAGE": "JSON",
            "Content-Type": "text/plain",
        },
        method="PUT",
    )

    with request.urlopen(test_request) as response:
        assert response.status == 204

    # Check that the spec is now listed
    test_request = request.Request(
        "https://package.api.openalchemy.io/v1/specs",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    with request.urlopen(test_request) as response:
        assert response.status == 200
        returned_specs = json.loads(response.read().decode())
        assert len(returned_specs) == 1
        returned_spec = returned_specs[0]
        assert returned_spec["name"] == spec_name
        assert returned_spec["id"] == spec_name.lower()
        assert returned_spec["version"] == version
        assert "updated_at" in returned_spec

    # Check that the version is listed
    test_request = request.Request(
        f"https://package.api.openalchemy.io/v1/specs/{spec_name}/versions",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    with request.urlopen(test_request) as response:
        assert response.status == 200
        returned_specs = json.loads(response.read().decode())
        assert len(returned_specs) == 1
        returned_spec = returned_specs[0]
        assert returned_spec["name"] == spec_name
        assert returned_spec["id"] == spec_name.lower()
        assert returned_spec["version"] == version
        assert "updated_at" in returned_spec

    # Check that the spec can be retrieved
    test_request = request.Request(
        f"https://package.api.openalchemy.io/v1/specs/{spec_name}/versions/{version}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    with request.urlopen(test_request) as response:
        assert response.status == 200
        response_json = json.loads(response.read().decode())
        spec_str = response_json["value"]
        assert version in spec_str
        assert "Schema:" in spec_str
        assert "x-tablename:" in spec_str
        assert ": schema" in spec_str
        assert response_json["name"] == spec_name
        assert response_json["id"] == spec_name.lower()
        assert response_json["version"] == version
        assert "updated_at" in response_json


def test_credentials_default_get_delete_get(access_token, credentials_id):
    """
    GIVEN credentials
    WHEN they are retrieved, deleted and retrieved again
    THEN the public and secret key are returned and are different after delete is
        called.
    """
    # Get the credentials
    test_request = request.Request(
        f"https://package.api.openalchemy.io/v1/credentials/{credentials_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    with request.urlopen(test_request) as response:
        assert response.status == 200
        response_data = json.loads(response.read().decode())
        assert "public_key" in response_data
        public_key = response_data["public_key"]
        assert "secret_key" in response_data
        secret_key = response_data["secret_key"]

    # Delete the credentials
    test_request = request.Request(
        f"https://package.api.openalchemy.io/v1/credentials/{credentials_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        method="DELETE",
    )

    with request.urlopen(test_request) as response:
        assert response.status == 204
    # Get the again credentials
    test_request = request.Request(
        f"https://package.api.openalchemy.io/v1/credentials/{credentials_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    with request.urlopen(test_request) as response:
        assert response.status == 200
        response_data = json.loads(response.read().decode())
        assert "public_key" in response_data
        assert response_data["public_key"] != public_key
        assert "secret_key" in response_data
        assert response_data["secret_key"] != secret_key
