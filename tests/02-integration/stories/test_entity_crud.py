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

            assert (
                key in retrieved_data
            ), f"SDO: {sdo}, Key {key} is not in retrieved_data"

            compare_data = retrieved_data[key]
            if isinstance(value, str):
                assert (
                    value == compare_data
                ), f"SDO: {sdo}, Key '{key}': {value} does't match {retrieved_data[key]} ({retrieved_data}"
            # else:
            # TODO compare other values types

    def test_create(self, fruit_bowl, api_client):
        for sdo, s_class in fruit_bowl.items():
            s_class.setup()
            test_indicator = s_class.ownclass().create(**s_class.data())
            assert test_indicator is not None, f"No ID on object {sdo}"
            assert "id" in test_indicator, f"No ID on object {sdo}"

            s_class.teardown()

    def test_read(self, fruit_bowl, api_client):
        for sdo, s_class in fruit_bowl.items():
            s_class.setup()
            test_indicator = s_class.ownclass().create(**s_class.data())
            assert test_indicator is not None, f"No ID on object {sdo}"
            assert "id" in test_indicator, f"No ID on object {sdo}"
            test_indicator = s_class.ownclass().read(id=test_indicator["id"])
            self.compare_values(sdo, s_class.data(), test_indicator)

            s_class.teardown()

    def test_update(self, fruit_bowl, api_client):
        for sdo, s_class in fruit_bowl.items():
            s_class.setup()
            obj = s_class.data()
            test_indicator = s_class.ownclass().create(**obj)
            assert test_indicator is not None, f"No ID on object {sdo}"
            assert "id" in test_indicator, f"No ID on object {sdo}"
            obj["description"] = "Test"
            obj["update"] = True
            result = s_class.ownclass().create(**obj)
            result = s_class.ownclass().read(id=result["id"])
            assert result["description"] == "Test"
            assert result["id"] == test_indicator["id"]

            s_class.teardown()

    def test_delete(self, fruit_bowl, api_client):
        for sdo, attributes in fruit_bowl.items():
            attributes.setup()
            obj = attributes.data()
            test_indicator = attributes.ownclass().create(**obj)
            assert test_indicator is not None, f"No ID on object {sdo}"
            assert "id" in test_indicator, f"No ID on object {sdo}"
            result = attributes.baseclass().delete(id=test_indicator["id"])
            assert result is None
            result = attributes.ownclass().read(id=test_indicator["id"])
            assert result is None

            attributes.teardown()

    def test_import_from_stix2(self, fruit_bowl, api_client):
        pass
