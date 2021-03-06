"""Tests for the models get_item."""

import pytest
from open_alchemy.package_database import exceptions, factory, models

GET_ITEM_MISS_TESTS = [
    pytest.param([], "sub 1", "name 1", id="empty"),
    pytest.param(
        [
            factory.SpecFactory(
                sub="sub 1",
                name="name 1",
                id="name 1",
                updated_at_id=f"{models.Spec.UPDATED_AT_LATEST}#name 1",
            )
        ],
        "sub 2",
        "name 1",
        id="single sub miss",
    ),
    pytest.param(
        [
            factory.SpecFactory(
                sub="sub 1",
                name="name 1",
                id="name 1",
                updated_at_id=f"{models.Spec.UPDATED_AT_LATEST}#name 1",
            )
        ],
        "sub 1",
        "name 2",
        id="single id miss",
    ),
]


@pytest.mark.parametrize("items, sub, name", GET_ITEM_MISS_TESTS)
@pytest.mark.models
def test_get_item_miss(items, sub, name):
    """
    GIVEN items in the database and sub and spec name
    WHEN get_item is called on Spec with the sub and spec name
    THEN the expected item is returned.
    """
    for item in items:
        item.save()

    with pytest.raises(exceptions.NotFoundError):
        models.Spec.get_item(sub=sub, name=name)


GET_ITEM_TESTS = [
    pytest.param(
        [
            factory.SpecFactory(
                sub="sub 1",
                name="name 1",
                id="name 1",
                updated_at_id=f"{models.Spec.UPDATED_AT_LATEST}#name 1",
            )
        ],
        "sub 1",
        "name 1",
        0,
        id="single hit",
    ),
    pytest.param(
        [
            factory.SpecFactory(
                sub="sub 1",
                name="NAME 1",
                id="name 1",
                updated_at_id=f"{models.Spec.UPDATED_AT_LATEST}#name 1",
            )
        ],
        "sub 1",
        "NAME 1",
        0,
        id="single hit different canonical name",
    ),
]


@pytest.mark.parametrize("items, sub, name, expected_item_index", GET_ITEM_TESTS)
@pytest.mark.models
def test_get_item(items, sub, name, expected_item_index):
    """
    GIVEN items in the database and sub and spec name
    WHEN get_item is called on Spec with the sub and spec name
    THEN the expected item is returned.
    """
    for item in items:
        item.save()

    returned_item = models.Spec.get_item(sub=sub, name=name)

    assert returned_item == models.Spec.item_to_info(items[expected_item_index])
