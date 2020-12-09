"""Tests for the API."""

import copy
import json
from urllib import request, error

import yaml
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
            "https://package.api.openalchemy.io/v1/specs/spec1/versions/version1",
            method="GET",
        ),
        request.Request(
            "https://package.api.openalchemy.io/v1/specs/spec1/versions/version1",
            data=b"data 1",
            method="PUT",
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


def test_specs_create_get_delete(access_token, spec_id):
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
    spec = {
        "components": {
            "schemas": {
                "Schema": {
                    "type": "object",
                    "x-tablename": "schema",
                    "properties": {"id": {"type": "integer"}},
                }
            }
        }
    }
    spec_str = json.dumps(spec)
    test_request = request.Request(
        f"https://package.api.openalchemy.io/v1/specs/{spec_id}",
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
        assert returned_spec["spec_id"] == spec_id
        assert "version" in returned_spec

    # Check that the spec can be retrieved
    test_request = request.Request(
        f"https://package.api.openalchemy.io/v1/specs/{spec_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    with request.urlopen(test_request) as response:
        assert response.status == 200
        spec_str = response.read().decode()
        assert "Schema:" in spec_str
        assert "x-tablename:" in spec_str
        assert ": schema" in spec_str

    # Delete the spec
    test_request = request.Request(
        f"https://package.api.openalchemy.io/v1/specs/{spec_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        method="DELETE",
    )

    with request.urlopen(test_request) as response:
        assert response.status == 204

    # Check that the spec can no longer be retrieved
    test_request = request.Request(
        f"https://package.api.openalchemy.io/v1/specs/{spec_id}",
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


def test_specs_versions_create_get_delete(access_token, spec_id):
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
    version = "version1"
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
        f"https://package.api.openalchemy.io/v1/specs/{spec_id}/versions/{version}",
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
        assert returned_spec["spec_id"] == spec_id
        assert returned_spec["version"] == version

    # Check that the version is listed
    test_request = request.Request(
        f"https://package.api.openalchemy.io/v1/specs/{spec_id}/versions",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    with request.urlopen(test_request) as response:
        assert response.status == 200
        assert json.loads(response.read().decode()) == [version]

    # Check that the spec can be retrieved
    test_request = request.Request(
        f"https://package.api.openalchemy.io/v1/specs/{spec_id}/versions/{version}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    with request.urlopen(test_request) as response:
        assert response.status == 200
        spec_str = response.read().decode()
        assert version in spec_str
        assert "Schema:" in spec_str
        assert "x-tablename:" in spec_str
        assert ": schema" in spec_str
