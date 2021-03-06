"""Tests for the app."""

import json
import pathlib
from unittest import mock

import app
import library
import pytest
from botocore import stub


def no_directory(_: pathlib.Path) -> None:
    """Does nothing."""


def directory_empty(path: pathlib.Path) -> None:
    """Creates empty directory."""
    (path / "build").mkdir()


def directory_with_single_file(path: pathlib.Path) -> None:
    """Creates empty directory."""
    directory_empty(path)
    (path / "build" / "test.txt").write_text("file 1")


def directory_with_multiple_file(path: pathlib.Path) -> None:
    """Creates empty directory."""
    directory_with_single_file(path)
    (path / "build" / "test.json").write_text("'value 1")


def file(path: pathlib.Path) -> None:
    """Creates a file."""
    (path / "build").write_text("file 1")


@pytest.mark.parametrize(
    "setup_steps",
    [
        pytest.param(no_directory, id="no directory"),
        pytest.param(directory_empty, id="directory exists"),
        pytest.param(
            directory_with_single_file,
            id="directory exists with single file",
        ),
        pytest.param(
            directory_with_multiple_file,
            id="directory exists with multiple file",
        ),
        pytest.param(file, id="file"),
    ],
)
def test_setup_not_exists(tmp_path, setup_steps):
    """
    GIVEN
    WHEN setup is called
    THEN the build folder is created and empty.
    """
    setup_steps(tmp_path)

    returned_path = app.setup(str(tmp_path))

    assert str(returned_path) == str(tmp_path / "build")
    assert returned_path.exists()
    assert next(returned_path.glob("**/*"), None) is None


PARSE_NOTIFICATION_ERROR_TESTS = [
    pytest.param(None, id="not dict"),
    pytest.param({}, id="Records missing"),
    pytest.param({"Records": True}, id="Records not list"),
    pytest.param({"Records": []}, id="Records empty"),
    pytest.param({"Records": [1, 2]}, id="Records multiple"),
    pytest.param({"Records": [None]}, id="Records not dict"),
    pytest.param({"Records": [{}]}, id="Records SNS missing"),
    pytest.param({"Records": [{"Sns": None}]}, id="Records SNS not dict"),
    pytest.param({"Records": [{"Sns": {}}]}, id="Records SNS Message missing"),
    pytest.param(
        {"Records": [{"Sns": {"Message": None}}]},
        id="Records SNS Message not string",
    ),
    pytest.param(
        {"Records": [{"Sns": {"Message": "value 1"}}]},
        id="Records SNS Message not JSON",
    ),
    pytest.param(
        {"Records": [{"Sns": {"Message": json.dumps("value 1")}}]},
        id="Records SNS Message JSON not dict",
    ),
    pytest.param(
        {"Records": [{"Sns": {"Message": json.dumps({})}}]},
        id="Records SNS Message JSON Records missing",
    ),
    pytest.param(
        {"Records": [{"Sns": {"Message": json.dumps({"Records": True})}}]},
        id="Records SNS Message JSON Records not list",
    ),
    pytest.param(
        {"Records": [{"Sns": {"Message": json.dumps({"Records": []})}}]},
        id="Records SNS Message JSON Records empty",
    ),
    pytest.param(
        {"Records": [{"Sns": {"Message": json.dumps({"Records": [1, 2]})}}]},
        id="Records SNS Message JSON Records multiple",
    ),
    pytest.param(
        {"Records": [{"Sns": {"Message": json.dumps({"Records": [True]})}}]},
        id="Records SNS Message JSON Records not dict",
    ),
    pytest.param(
        {"Records": [{"Sns": {"Message": json.dumps({"Records": [{}]})}}]},
        id="Records SNS Message JSON Records s3 missing",
    ),
    pytest.param(
        {"Records": [{"Sns": {"Message": json.dumps({"Records": [{"s3": True}]})}}]},
        id="Records SNS Message JSON Records s3 not dict",
    ),
    pytest.param(
        {
            "Records": [
                {
                    "Sns": {
                        "Message": json.dumps(
                            {"Records": [{"s3": {"object": {"key": "key 1"}}}]}
                        )
                    }
                }
            ]
        },
        id="Records SNS Message JSON Records s3 bucket missing",
    ),
    pytest.param(
        {
            "Records": [
                {
                    "Sns": {
                        "Message": json.dumps(
                            {
                                "Records": [
                                    {
                                        "s3": {
                                            "bucket": True,
                                            "object": {"key": "key 1"},
                                        }
                                    }
                                ]
                            }
                        )
                    }
                }
            ]
        },
        id="Records SNS Message JSON Records s3 bucket not dict",
    ),
    pytest.param(
        {
            "Records": [
                {
                    "Sns": {
                        "Message": json.dumps(
                            {
                                "Records": [
                                    {
                                        "s3": {
                                            "bucket": {},
                                            "object": {"key": "key 1"},
                                        }
                                    }
                                ]
                            }
                        )
                    }
                }
            ]
        },
        id="Records SNS Message JSON Records s3 bucket name missing",
    ),
    pytest.param(
        {
            "Records": [
                {
                    "Sns": {
                        "Message": json.dumps(
                            {
                                "Records": [
                                    {
                                        "s3": {
                                            "bucket": {"name": True},
                                            "object": {"key": "key 1"},
                                        }
                                    }
                                ]
                            }
                        )
                    }
                }
            ]
        },
        id="Records SNS Message JSON Records s3 bucket name not string",
    ),
    pytest.param(
        {
            "Records": [
                {
                    "Sns": {
                        "Message": json.dumps(
                            {"Records": [{"s3": {"bucket": {"name": "bucket 1"}}}]}
                        )
                    }
                }
            ]
        },
        id="Records SNS Message JSON Records s3 object missing",
    ),
    pytest.param(
        {
            "Records": [
                {
                    "Sns": {
                        "Message": json.dumps(
                            {
                                "Records": [
                                    {
                                        "s3": {
                                            "bucket": {"name": "bucket 1"},
                                            "object": True,
                                        }
                                    }
                                ]
                            }
                        )
                    }
                }
            ]
        },
        id="Records SNS Message JSON Records s3 object not dict",
    ),
    pytest.param(
        {
            "Records": [
                {
                    "Sns": {
                        "Message": json.dumps(
                            {
                                "Records": [
                                    {
                                        "s3": {
                                            "bucket": {"name": "bucket 1"},
                                            "object": {},
                                        }
                                    }
                                ]
                            }
                        )
                    }
                }
            ]
        },
        id="Records SNS Message JSON Records s3 object key missing",
    ),
    pytest.param(
        {
            "Records": [
                {
                    "Sns": {
                        "Message": json.dumps(
                            {
                                "Records": [
                                    {
                                        "s3": {
                                            "bucket": {"name": "bucket 1"},
                                            "object": {"key": True},
                                        }
                                    }
                                ]
                            }
                        )
                    }
                }
            ]
        },
        id="Records SNS Message JSON Records s3 object key not string",
    ),
]


@pytest.mark.parametrize("event", PARSE_NOTIFICATION_ERROR_TESTS)
def test_parse_event_error(event):
    """
    GIVEN event that is not valid
    WHEN parse_event is called with the event
    THEN AssertionError is raised.
    """
    with pytest.raises(AssertionError):
        app.parse_event(event)


def test_parse_event():
    """
    GIVEN lambda event
    WHEN parse_event is called with the event
    THEN the bucket name and object key are returned.
    """
    event = {
        "Records": [
            {
                "Sns": {
                    "Message": json.dumps(
                        {
                            "Records": [
                                {
                                    "s3": {
                                        "bucket": {"name": "bucket+1"},
                                        "object": {"key": "key+1"},
                                    }
                                }
                            ]
                        }
                    )
                }
            }
        ]
    }

    returned_notification = app.parse_event(event)

    assert returned_notification.bucket_name == "bucket 1"
    assert returned_notification.object_key == "key 1"


def test_retrieve_spec(tmp_path, monkeypatch):
    """
    GIVEN notification, build path and stubbed s3 download_file
    WHEN retrieve_spec is called
    THEN download_file was called with the correct parameters and the expected path is
        returned.
    """
    bucket_name = "bucket1"
    object_key = "key 1"
    notification = app.Notification(bucket_name=bucket_name, object_key=object_key)
    spec_path = tmp_path / "spec.json"
    mock_download_file = mock.MagicMock()
    monkeypatch.setattr(app.S3_CLIENT, "download_file", mock_download_file)

    returned_path = app.retrieve_spec(notification, tmp_path)

    assert str(returned_path) == str(spec_path)

    mock_download_file.assert_called_once_with(bucket_name, object_key, str(spec_path))


def test_upload_packages(monkeypatch):
    """
    GIVEN notification and packages
    WHEN upload_packages is called with the notification and packages
    THEN the packages are uploaded.
    """
    bucket_name = "bucket1"
    object_key = "key 1"
    notification = app.Notification(bucket_name=bucket_name, object_key=object_key)
    packages = [
        library.Package(
            storage_location="storage location 1",
            path=pathlib.Path("some/location1.tar.gz"),
        ),
        library.Package(
            storage_location="storage location 2",
            path=pathlib.Path("some/location2.tar.gz"),
        ),
    ]
    mock_upload_file = mock.MagicMock()
    monkeypatch.setattr(app.S3_CLIENT, "upload_file", mock_upload_file)

    app.upload_packages(notification, packages)

    assert mock_upload_file.call_count == 2
    mock_upload_file.assert_any_call(
        str(packages[0].path), bucket_name, packages[0].storage_location
    )
    mock_upload_file.assert_any_call(
        str(packages[1].path), bucket_name, packages[1].storage_location
    )


SPEC_EXISTS_ERROR_TESTS = [
    pytest.param(None, id="response not dict"),
    pytest.param({}, id="response KeyCount missing"),
    pytest.param({"KeyCount": None}, id="response KeyCount not int"),
]


@pytest.mark.parametrize("response", SPEC_EXISTS_ERROR_TESTS)
def test_spec_exists_error(monkeypatch, response):
    """
    GIVEN monkeypatched list_objects_v2 that returns invalid response
    WHEN spec_exists is called
    THEN AssertionError is raised.
    """
    bucket_name = "bucket1"
    object_key = "key 1"
    notification = app.Notification(bucket_name=bucket_name, object_key=object_key)

    mock_list_objects_v2 = mock.MagicMock()
    mock_list_objects_v2.return_value = response
    monkeypatch.setattr(app.S3_CLIENT, "list_objects_v2", mock_list_objects_v2)

    with pytest.raises(AssertionError):
        app.spec_exists(notification)


@pytest.mark.parametrize(
    "response, expected_result",
    [
        pytest.param({"KeyCount": 0}, False, id="key count 0"),
        pytest.param({"KeyCount": 1}, True, id="key count 1"),
        pytest.param({"KeyCount": 2}, False, id="key count > 1"),
    ],
)
def test_spec_exists(response, expected_result, stubbed_s3_client: stub.Stubber):
    """
    GIVEN notification and mocked S3 client that returns response
    WHEN spec_exists is called with the notification
    THEN the expected result is returned.
    """
    bucket_name = "bucket1"
    object_key = "key 1"
    notification = app.Notification(bucket_name=bucket_name, object_key=object_key)

    expected_params = {"Bucket": bucket_name, "Prefix": object_key}
    stubbed_s3_client.add_response("list_objects_v2", response, expected_params)
    stubbed_s3_client.activate()

    returned_result = app.spec_exists(notification)

    stubbed_s3_client.assert_no_pending_responses()
    assert returned_result == expected_result


@pytest.mark.parametrize(
    "spec_exists_result, expected_call_count",
    [
        pytest.param(True, 0, id="spec exists"),
        pytest.param(False, 1, id="spec not exists"),
    ],
)
def test_delete_packages_if_spec_deleted_mocked(
    spec_exists_result, expected_call_count, monkeypatch
):
    """
    GIVEN monkeypatched delete_objects and spec exists result
    WHEN delete_packages_if_spec_deleted is called
    THEN delete_objects is called the expected number of times.
    """
    bucket_name = "bucket1"
    object_key = "key 1"
    notification = app.Notification(bucket_name=bucket_name, object_key=object_key)
    packages = []

    mock_delete_objects = mock.MagicMock()
    monkeypatch.setattr(app.S3_CLIENT, "delete_objects", mock_delete_objects)

    app.delete_packages_if_spec_deleted(spec_exists_result, notification, packages)

    assert mock_delete_objects.call_count == expected_call_count


def test_delete_packages_if_spec_deleted(stubbed_s3_client: stub.Stubber):
    """
    GIVEN notification, packages and mocked S3 client
    WHEN delete_packages_if_spec_deleted is called with the notification and packages
    THEN delete objects is called.
    """
    bucket_name = "bucket1"
    object_key = "key 1"
    notification = app.Notification(bucket_name=bucket_name, object_key=object_key)
    packages = [
        library.Package(
            storage_location="storage location 1",
            path=pathlib.Path("some/location1.tar.gz"),
        ),
        library.Package(
            storage_location="storage location 2",
            path=pathlib.Path("some/location2.tar.gz"),
        ),
    ]

    expected_params = {
        "Bucket": bucket_name,
        "Delete": {
            "Objects": [{"Key": package.storage_location} for package in packages]
        },
    }
    stubbed_s3_client.add_response("delete_objects", {}, expected_params)
    stubbed_s3_client.activate()

    app.delete_packages_if_spec_deleted(False, notification, packages)

    stubbed_s3_client.assert_no_pending_responses()
