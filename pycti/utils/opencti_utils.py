class OpenCTIUtils:
    @staticmethod
    def build_marking_filter(markings: list[str], source_entity_id: str | None, objects_ids: list[str] | None):
        marking_filter = {
            "mode": "and",
            "filters": [],
            "filterGroups": [
                {
                    "mode": "or",
                    "filterGroups": [],
                    "filters": [
                        {
                            "key": "objectMarking",
                            "mode": "or",
                            "operator": "eq",
                            "values": markings,
                        },
                        {
                            "key": "objectMarking",
                            "mode": "or",
                            "operator": "nil",
                            "values": [],
                        },
                    ],
                }
            ],
        }
        source_entity_filter = {
            "key": "regardingOf",
            "mode": "and",
            "operator": "eq",
            "values": [
                {
                    "key": "id",
                    "values": [
                        source_entity_id
                    ]
                }
            ],
        }
        objects_ids_filter = {
            "key": "id",
            "mode": "or",
            "operator": "eq",
            "values": objects_ids,
        }

        if objects_ids is None or len(objects_ids) == 0:
            marking_filter["filters"].append(source_entity_filter)
            return marking_filter

        marking_filter["filters"].append(objects_ids_filter)
        return marking_filter
