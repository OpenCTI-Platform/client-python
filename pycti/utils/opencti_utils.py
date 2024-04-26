class OpenCTIUtils:
    @staticmethod
    def build_marking_filter(objects_ids: list[str] | None, markings: list[str]):
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
        objects_ids_filter = {
            "key": "id",
            "mode": "or",
            "operator": "eq",
            "values": objects_ids,
        }

        if objects_ids is None or len(objects_ids) == 0:
            return marking_filter

        marking_filter["filters"] = objects_ids_filter
        return marking_filter
