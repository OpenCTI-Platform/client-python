from pytest_cases import parametrize_with_cases, fixture
from tests.cases.entities import EntityTestCases
from tests.utils import compare_values


@fixture
@parametrize_with_cases("entity", cases=EntityTestCases)
def entity_class(entity):
    entity.setup()
    yield entity
    entity.teardown()


def test_entity_create(entity_class):
    class_data = entity_class.data()
    test_indicator = entity_class.ownclass().create(**class_data)
    assert test_indicator is not None, "Response is NoneType"
    assert "id" in test_indicator, "No ID on object"

    entity_class.baseclass().delete(id=test_indicator["id"])


def test_read(entity_class):
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


def test_update(entity_class):
    class_data = entity_class.data()
    test_indicator = entity_class.ownclass().create(**class_data)
    assert test_indicator is not None, "Response is NoneType"
    assert "id" in test_indicator, "No ID on object"

    if len(entity_class.update_data()) > 0:
        function_present = getattr(entity_class.ownclass(), "update_field", None)
        if function_present:
            for update_field, update_value in entity_class.update_data().items():
                class_data[update_field] = update_value
                input = [{"key": update_field, "value": str(update_value)}]
                result = entity_class.ownclass().update_field(
                    id=test_indicator["id"], input=input
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


def test_delete(entity_class):
    class_data = entity_class.data()
    test_indicator = entity_class.ownclass().create(**class_data)
    assert test_indicator is not None, "Response is NoneType"
    assert "id" in test_indicator, "No ID on object"
    result = entity_class.baseclass().delete(id=test_indicator["id"])
    assert result is None, f"Delete returned value '{result}'"
    result = entity_class.ownclass().read(id=test_indicator["id"])
    assert result is None, f"Read returned value '{result}' after delete"


def test_filter(entity_class):
    if len(entity_class.get_filter()) == 0:
        return

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
