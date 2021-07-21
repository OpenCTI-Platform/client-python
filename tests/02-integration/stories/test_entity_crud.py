from typing import Dict, List
from pytest_cases import parametrize_with_cases
from tests.modules.entities import EntityTestCases


def compare_values(original_data: Dict, retrieved_data: Dict, exception_keys: List):
    for key, value in original_data.items():
        # Attributes which aren't present in the final Stix objects
        if key in exception_keys:
            continue

        assert key in retrieved_data, f"Key {key} is not in retrieved_data"

        compare_data = retrieved_data.get(key, None)
        if isinstance(value, str):
            assert (
                value == compare_data
            ), f"Key '{key}': '{value}' does't match value '{retrieved_data[key]}' ({retrieved_data}"
        elif key == "objects" and isinstance(value, list):
            assert isinstance(compare_data, list), f"Key '{key}': is not a list"
            original_ids = set()
            for elem in value:
                if isinstance(elem, dict):
                    original_ids.add(elem.get("id", None))
                elif isinstance(elem, str):
                    original_ids.add(elem)

            retrieved_ids = set()
            for elem in compare_data:
                if isinstance(elem, dict):
                    retrieved_ids.add(elem.get("id", None))
                elif isinstance(elem, str):
                    original_ids.add(elem)

            assert (
                original_ids == retrieved_ids
            ), f"Key '{key}': '{value}' does't match value '{compare_data}'"
        elif isinstance(value, dict):
            assert len(value) == len(
                compare_data
            ), f"Dict '{value}' does not have the same length as '{compare_data}'"
            assert (
                value == compare_data
            ), f"Dict '{value}' does not have the same content as'{compare_data}'"


@parametrize_with_cases("entity_class", cases=EntityTestCases)
def test_entity_create(entity_class):
    entity_class.setup()
    class_data = entity_class.data()
    test_indicator = entity_class.ownclass().create(**class_data)
    assert test_indicator is not None, "Response is NoneType"
    assert "id" in test_indicator, "No ID on object"

    entity_class.baseclass().delete(id=test_indicator["id"])
    entity_class.teardown()


@parametrize_with_cases("entity_class", cases=EntityTestCases)
def test_read(entity_class):
    entity_class.setup()
    class_data = entity_class.data()
    test_indicator = entity_class.ownclass().create(**class_data)
    assert test_indicator is not None, "Response is NoneType"
    assert "id" in test_indicator, "No ID on object"
    test_indicator = entity_class.ownclass().read(id=test_indicator["id"])
    compare_values(
        class_data,
        test_indicator,
        entity_class.get_compare_exception_keys(),
    )

    entity_class.baseclass().delete(id=test_indicator["id"])
    entity_class.teardown()


@parametrize_with_cases("entity_class", cases=EntityTestCases)
def test_update(entity_class):
    entity_class.setup()

    class_data = entity_class.data()
    test_indicator = entity_class.ownclass().create(**class_data)
    assert test_indicator is not None, "Response is NoneType"
    assert "id" in test_indicator, "No ID on object"

    if len(entity_class.update_data()) > 0:
        function_present = getattr(entity_class.ownclass(), "update_field", None)
        if function_present:
            for update_field, update_value in entity_class.update_data().items():
                class_data[update_field] = update_value
                result = entity_class.ownclass().update_field(
                    id=test_indicator["id"],
                    key=update_field,
                    value=update_value,
                )
        else:
            for update_field, update_value in entity_class.update_data().items():
                class_data[update_field] = update_value
            class_data["update"] = True
            result = entity_class.ownclass().create(**class_data)

        result = entity_class.ownclass().read(id=result["id"])
        assert result["id"] == test_indicator["id"], "Updated SDO does not match old ID"
        compare_values(class_data, result, entity_class.get_compare_exception_keys())
    else:
        result = test_indicator

    entity_class.baseclass().delete(id=result["id"])
    entity_class.teardown()


@parametrize_with_cases("entity_class", cases=EntityTestCases)
def test_delete(entity_class):
    entity_class.setup()
    class_data = entity_class.data()
    test_indicator = entity_class.ownclass().create(**class_data)
    assert test_indicator is not None, "Response is NoneType"
    assert "id" in test_indicator, "No ID on object"
    result = entity_class.baseclass().delete(id=test_indicator["id"])
    assert result is None, f"Delete returned value '{result}'"
    result = entity_class.ownclass().read(id=test_indicator["id"])
    assert result is None, f"Read returned value '{result}' after delete"

    entity_class.teardown()


@parametrize_with_cases("entity_class", cases=EntityTestCases)
def test_filter(entity_class):
    if len(entity_class.get_filter()) == 0:
        return

    entity_class.setup()
    class_data = entity_class.data()
    test_indicator = entity_class.ownclass().create(**class_data)
    assert test_indicator is not None, "Response is NoneType"
    assert "id" in test_indicator, "No ID on object"
    test_indicator = entity_class.ownclass().read(filters=entity_class.get_filter())
    compare_values(
        class_data,
        test_indicator,
        entity_class.get_compare_exception_keys(),
    )

    entity_class.baseclass().delete(id=test_indicator["id"])
    entity_class.teardown()
