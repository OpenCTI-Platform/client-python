from typing import Dict, List


class Test_entity_crud:
    @staticmethod
    def compare_values(
        sdo: str, original_data: Dict, retrieved_data: Dict, exception_keys: List = None
    ):
        for key, value in original_data.items():
            # Attributes which aren't present in the final Stix objects
            if key in ["type", "update", "createdBy"]:
                continue
            if exception_keys and key in exception_keys:
                continue

            assert key in retrieved_data, f"{sdo}: Key {key} is not in retrieved_data"

            compare_data = retrieved_data[key]
            if isinstance(value, str):
                assert (
                    value == compare_data
                ), f"{sdo}: Key '{key}': {value} does't match {retrieved_data[key]} ({retrieved_data}"
            elif isinstance(value, list):
                assert len(value) == len(
                    compare_data
                ), f"{sdo}: List '{value}' does not have the same length as '{compare_data}'"
                for value_key in value:
                    assert (
                        value_key in compare_data
                    ), f"{sdo}: List '{compare_data}' does not contain '{value_key}'"
            # TODO compare other values types

    def test_create(self, fruit_bowl, api_client):
        for sdo, s_class in fruit_bowl.items():
            s_class.setup()
            for class_data in s_class.data():
                test_indicator = s_class.ownclass().create(**class_data)
                assert test_indicator is not None, f"{sdo}: No ID on object"
                assert "id" in test_indicator, f"{sdo}: No ID on object"

            s_class.teardown()

    def test_read(self, fruit_bowl, api_client):
        for sdo, s_class in fruit_bowl.items():
            s_class.setup()
            for class_data in s_class.data():
                test_indicator = s_class.ownclass().create(**class_data)
                assert test_indicator is not None, f"{sdo}: No ID on object"
                assert "id" in test_indicator, f"{sdo}: No ID on object"
                test_indicator = s_class.ownclass().read(id=test_indicator["id"])
                self.compare_values(sdo, class_data, test_indicator)

            s_class.teardown()

    def test_update(self, fruit_bowl, api_client):
        for sdo, s_class in fruit_bowl.items():
            s_class.setup()
            for class_data in s_class.data():
                test_indicator = s_class.ownclass().create(**class_data)
                assert test_indicator is not None, f"{sdo}: No ID on object"
                assert "id" in test_indicator, f"{sdo}: No ID on object"

                update_field = ""
                if "description" in class_data:
                    update_field = "description"
                elif sdo == "Note":
                    update_field = "content"

                class_data[update_field] = "Test"
                class_data["update"] = True
                result = s_class.ownclass().create(**class_data)
                result = s_class.ownclass().read(id=result["id"])
                assert (
                    result[update_field] == "Test"
                ), f"{sdo}: Updated field {update_field} is not 'Test', instead{result[update_field]}"
                assert (
                    result["id"] == test_indicator["id"]
                ), f"{sdo}: Updated SDO ID does not match old ID"

            s_class.teardown()

    def test_delete(self, fruit_bowl, api_client):
        for sdo, s_class in fruit_bowl.items():
            s_class.setup()
            for class_data in s_class.data():
                test_indicator = s_class.ownclass().create(**class_data)
                assert test_indicator is not None, f"{sdo}: No ID on object"
                assert "id" in test_indicator, f"{sdo}: No ID on object"
                result = s_class.baseclass().delete(id=test_indicator["id"])
                assert result is None, f"{sdo}: Delete returned value '{result}'"
                result = s_class.ownclass().read(id=test_indicator["id"])
                assert (
                    result is None
                ), f"{sdo}: Read returned value '{result}' after delete"

            s_class.teardown()

    def test_import_from_stix2(self, fruit_bowl, api_client):
        pass
