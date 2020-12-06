"""Tests for the specs endpoint."""

import json
from unittest import mock

import pytest

from library import specs
from library.facades import storage, server, database


def test_list_(_clean_package_storage_table):
    """
    GIVEN user and database with a single spec
    WHEN list_ is called with the user
    THEN all the specs stored on the user are returned.
    """
    user = "user 1"
    spec_id = "spec id 1"
    database.get_database().create_update_spec(
        sub=user, spec_id=spec_id, version="version 1", model_count=1
    )

    response = specs.list_(user=user)

    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert json.loads(response.data.decode()) == [spec_id]


def test_list_miss(_clean_package_storage_table):
    """
    GIVEN user and database with a single spec for a different user
    WHEN list_ is called with the user
    THEN empty list is returned.
    """
    user = "user 1"
    spec_id = "spec id 1"
    database.get_database().create_update_spec(
        sub="user 2", spec_id=spec_id, version="version 1", model_count=1
    )

    response = specs.list_(user=user)

    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert json.loads(response.data.decode()) == []


def test_list_database_error(monkeypatch):
    """
    GIVEN user and database that raises a DatabaseError
    WHEN list_ is called with the user
    THEN a 500 is returned.
    """
    user = "user 1"
    spec_id = "spec id 1"
    mock_database_list_specs = mock.MagicMock()
    mock_database_list_specs.side_effect = database.exceptions.DatabaseError
    monkeypatch.setattr(
        database.get_database(),
        "list_specs",
        mock_database_list_specs,
    )

    response = specs.list_(user=user)

    assert response.status_code == 500
    assert response.mimetype == "text/plain"
    assert "database" in response.data.decode()


def test_get(_clean_package_storage_table):
    """
    GIVEN user and database and storage with a single spec
    WHEN get is called with the user and spec id
    THEN the spec value is returned.
    """
    user = "user 1"
    spec_id = "spec id 1"
    version = "version 1"
    database.get_database().create_update_spec(
        sub=user, spec_id=spec_id, version=version, model_count=1
    )
    spec = {"key": "value"}
    storage.get_storage_facade().create_update_spec(
        user=user,
        spec_id=spec_id,
        version=version,
        spec_str=json.dumps(spec, separators=(",", ":")),
    )

    response = specs.get(user=user, spec_id=spec_id)

    assert response.status_code == 200
    assert response.mimetype == "text/plain"
    assert f"version: {version}" in response.data.decode()
    assert f"key: value" in response.data.decode()


def test_get_database_error(_clean_package_storage_table, monkeypatch):
    """
    GIVEN user and database that raises an error
    WHEN get is called with the user and spec id
    THEN a 500 is returned.
    """
    user = "user 1"
    spec_id = "spec id 1"
    mock_database_get_latest_spec_version = mock.MagicMock()
    mock_database_get_latest_spec_version.side_effect = (
        database.exceptions.DatabaseError
    )
    monkeypatch.setattr(
        database.get_database(),
        "get_latest_spec_version",
        mock_database_get_latest_spec_version,
    )

    response = specs.get(user=user, spec_id=spec_id)

    assert response.status_code == 500
    assert response.mimetype == "text/plain"
    assert "database" in response.data.decode()


def test_get_database_miss(_clean_package_storage_table):
    """
    GIVEN user and empty database
    WHEN get is called with the user and spec id
    THEN a 404 is returned.
    """
    user = "user 1"
    spec_id = "spec id 1"

    response = specs.get(user=user, spec_id=spec_id)

    assert response.status_code == 404
    assert response.mimetype == "text/plain"
    assert spec_id in response.data.decode()
    assert "not find" in response.data.decode()


def test_get_storage_facade_error(_clean_package_storage_table, monkeypatch):
    """
    GIVEN user and database with a spec but storage that raises an error
    WHEN get is called with the user and spec id
    THEN a 500 is returned.
    """
    user = "user 1"
    spec_id = "spec id 1"
    version = "version 1"
    database.get_database().create_update_spec(
        sub=user, spec_id=spec_id, version=version, model_count=1
    )
    mock_storage_get_spec = mock.MagicMock()
    mock_storage_get_spec.side_effect = storage.exceptions.StorageError
    monkeypatch.setattr(storage.get_storage_facade(), "get_spec", mock_storage_get_spec)

    response = specs.get(user=user, spec_id=spec_id)

    assert response.status_code == 500
    assert response.mimetype == "text/plain"
    assert "reading" in response.data.decode()


def test_get_storage_facade_miss(_clean_package_storage_table):
    """
    GIVEN user and database with a spec but empty storage
    WHEN get is called with the user and spec id
    THEN a 404 is returned.
    """
    user = "user 1"
    spec_id = "spec id 1"
    version = "version 1"
    database.get_database().create_update_spec(
        sub=user, spec_id=spec_id, version=version, model_count=1
    )

    response = specs.get(user=user, spec_id=spec_id)

    assert response.status_code == 404
    assert response.mimetype == "text/plain"
    assert spec_id in response.data.decode()
    assert "not find" in response.data.decode()


def test_put(monkeypatch, _clean_package_storage_table):
    """
    GIVEN body, spec id and user
    WHEN put is called with the body, spec id and user
    THEN the spec is stored against the spec id.
    """
    mock_request = mock.MagicMock()
    mock_headers = {"X-LANGUAGE": "JSON"}
    mock_request.headers = mock_headers
    monkeypatch.setattr(server.Request, "request", mock_request)
    version = "version 1"
    schemas = {
        "Schema": {
            "type": "object",
            "x-tablename": "schema",
            "properties": {"id": {"type": "integer"}},
        }
    }
    body = json.dumps(
        {"info": {"version": version}, "components": {"schemas": schemas}}
    )
    spec_id = "id 1"
    user = "user 1"

    response = specs.put(body=body.encode(), spec_id=spec_id, user=user)

    assert storage.get_storage_facade().get_spec(
        user=user, spec_id=spec_id, version=version
    ) == json.dumps({"components": {"schemas": schemas}}, separators=(",", ":"))
    assert database.get_database().count_customer_models(sub=user) == 1
    assert response.status_code == 204


def test_put_invalid_spec_error(monkeypatch):
    """
    GIVEN body with invalid spec and spec id and user
    WHEN put is called with the body, spec id and user
    THEN a 400 with an invalid spec is returned.
    """
    mock_request = mock.MagicMock()
    mock_headers = {"X-LANGUAGE": "JSON"}
    mock_request.headers = mock_headers
    monkeypatch.setattr(server.Request, "request", mock_request)
    body = "body 1"
    spec_id = "id 1"
    user = "user 1"

    response = specs.put(body=body.encode(), spec_id=spec_id, user=user)

    assert response.status_code == 400
    assert response.mimetype == "text/plain"
    assert "not valid" in response.data.decode()


def test_put_too_many_models_error(monkeypatch, _clean_package_storage_table):
    """
    GIVEN body spec and spec id and user that already has too many models
    WHEN put is called with the body and spec id
    THEN a 402 with an invalid spec is returned.
    """
    mock_request = mock.MagicMock()
    mock_headers = {"X-LANGUAGE": "JSON"}
    mock_request.headers = mock_headers
    monkeypatch.setattr(server.Request, "request", mock_request)
    version = "version 1"
    schemas = {
        "Schema": {
            "type": "object",
            "x-tablename": "schema",
            "properties": {"id": {"type": "integer"}},
        }
    }
    body = json.dumps(
        {"info": {"version": version}, "components": {"schemas": schemas}}
    )
    spec_id = "id 1"
    user = "user 1"
    database.get_database().create_update_spec(
        sub=user, spec_id=spec_id, version="version 1", model_count=100
    )

    response = specs.put(body=body.encode(), spec_id=spec_id, user=user)

    assert response.status_code == 402
    assert response.mimetype == "text/plain"
    assert "exceeded" in response.data.decode()
    assert ": 100," in response.data.decode()
    assert "spec: 1" in response.data.decode()


def test_put_database_count_error(monkeypatch, _clean_package_storage_table):
    """
    GIVEN body with invalid spec and spec id and database that raises DatabaseError
    WHEN put is called with the body and spec id
    THEN a 500 is returned.
    """
    mock_request = mock.MagicMock()
    mock_headers = {"X-LANGUAGE": "JSON"}
    mock_request.headers = mock_headers
    monkeypatch.setattr(server.Request, "request", mock_request)
    version = "version 1"
    schemas = {
        "Schema": {
            "type": "object",
            "x-tablename": "schema",
            "properties": {"id": {"type": "integer"}},
        }
    }
    body = json.dumps(
        {"info": {"version": version}, "components": {"schemas": schemas}}
    )
    spec_id = "id 1"
    user = "user 1"
    mock_database_check_would_exceed_free_tier = mock.MagicMock()
    mock_database_check_would_exceed_free_tier.side_effect = (
        database.exceptions.DatabaseError
    )
    monkeypatch.setattr(
        database.get_database(),
        "check_would_exceed_free_tier",
        mock_database_check_would_exceed_free_tier,
    )

    response = specs.put(body=body.encode(), spec_id=spec_id, user=user)

    assert response.status_code == 500
    assert response.mimetype == "text/plain"
    assert "database" in response.data.decode()


def test_put_storage_error(monkeypatch, _clean_package_storage_table):
    """
    GIVEN body with invalid spec and spec id
    WHEN put is called with the body and spec id
    THEN a 400 with an invalid spec is returned.
    """
    mock_request = mock.MagicMock()
    mock_headers = {"X-LANGUAGE": "JSON"}
    mock_request.headers = mock_headers
    monkeypatch.setattr(server.Request, "request", mock_request)
    version = "version 1"
    schemas = {
        "Schema": {
            "type": "object",
            "x-tablename": "schema",
            "properties": {"id": {"type": "integer"}},
        }
    }
    body = json.dumps(
        {"info": {"version": version}, "components": {"schemas": schemas}}
    )
    spec_id = "id 1"
    user = "user 1"
    mock_storage_create_update_spec = mock.MagicMock()
    mock_storage_create_update_spec.side_effect = storage.exceptions.StorageError
    monkeypatch.setattr(
        storage.get_storage_facade(),
        "create_update_spec",
        mock_storage_create_update_spec,
    )

    response = specs.put(body=body.encode(), spec_id=spec_id, user=user)

    assert response.status_code == 500
    assert response.mimetype == "text/plain"
    assert "storing" in response.data.decode()


def test_put_database_update_error(monkeypatch, _clean_package_storage_table):
    """
    GIVEN body and spec id
    WHEN put is called with the body and spec id
    THEN the spec is stored against the spec id.
    """
    mock_request = mock.MagicMock()
    mock_headers = {"X-LANGUAGE": "JSON"}
    mock_request.headers = mock_headers
    monkeypatch.setattr(server.Request, "request", mock_request)
    version = "version 1"
    schemas = {
        "Schema": {
            "type": "object",
            "x-tablename": "schema",
            "properties": {"id": {"type": "integer"}},
        }
    }
    body = json.dumps(
        {"info": {"version": version}, "components": {"schemas": schemas}}
    )
    spec_id = "id 1"
    user = "user 1"
    mock_database_create_update_spec = mock.MagicMock()
    mock_database_create_update_spec.side_effect = database.exceptions.DatabaseError
    monkeypatch.setattr(
        database.get_database(),
        "create_update_spec",
        mock_database_create_update_spec,
    )

    response = specs.put(body=body.encode(), spec_id=spec_id, user=user)

    assert storage.get_storage_facade().get_spec(
        user=user, spec_id=spec_id, version=version
    ) == json.dumps({"components": {"schemas": schemas}}, separators=(",", ":"))
    assert database.get_database().count_customer_models(sub=user) == 0
    assert response.status_code == 500
    assert response.mimetype == "text/plain"
    assert "database" in response.data.decode()


def test_delete(_clean_package_storage_table):
    """
    GIVEN database and storage with spec and user and spec id
    WHEN put is called with the body and spec id
    THEN the spec is deleted from the storage and database.
    """
    spec_id = "id 1"
    user = "user 1"
    version = "version 1"
    database.get_database().create_update_spec(
        sub=user, spec_id=spec_id, version=version, model_count=1
    )
    storage.get_storage_facade().create_update_spec(
        user=user, spec_id=spec_id, version=version, spec_str="spec str 1"
    )

    response = specs.delete(spec_id=spec_id, user=user)

    with pytest.raises(storage.exceptions.StorageError):
        storage.get_storage_facade().get_spec(
            user=user, spec_id=spec_id, version=version
        )
    assert database.get_database().count_customer_models(sub=user) == 0
    assert response.status_code == 204


def test_delete_database_error(monkeypatch, _clean_package_storage_table):
    """
    GIVEN database that raises a DatabaseError and storage with spec and user and spec
        id
    WHEN put is called with the body and spec id
    THEN the spec is deleted from the storage.
    """
    spec_id = "id 1"
    user = "user 1"
    version = "version 1"
    mock_database_delete_spec = mock.MagicMock()
    mock_database_delete_spec.side_effect = database.exceptions.DatabaseError
    monkeypatch.setattr(
        database.get_database(),
        "delete_spec",
        mock_database_delete_spec,
    )
    storage.get_storage_facade().create_update_spec(
        user=user, spec_id=spec_id, version=version, spec_str="spec str 1"
    )

    response = specs.delete(spec_id=spec_id, user=user)

    with pytest.raises(storage.exceptions.StorageError):
        storage.get_storage_facade().get_spec(
            user=user, spec_id=spec_id, version=version
        )
    assert response.status_code == 204


def test_delete_database_error(monkeypatch, _clean_package_storage_table):
    """
    GIVEN database and storage that raises a StorageError with spec and user and spec
        id
    WHEN put is called with the body and spec id
    THEN the spec is deleted from the database.
    """
    spec_id = "id 1"
    user = "user 1"
    version = "version 1"
    database.get_database().create_update_spec(
        sub=user, spec_id=spec_id, version=version, model_count=1
    )
    mock_storage_delete_spec = mock.MagicMock()
    mock_storage_delete_spec.side_effect = storage.exceptions.StorageError
    monkeypatch.setattr(
        storage.get_storage_facade(),
        "delete_spec",
        mock_storage_delete_spec,
    )

    response = specs.delete(spec_id=spec_id, user=user)

    assert database.get_database().count_customer_models(sub=user) == 0
    assert response.status_code == 204