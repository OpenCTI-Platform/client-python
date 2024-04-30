import json
import re
import uuid
from typing import Tuple

from typing_extensions import deprecated

MITRE_X_CAPEC = (
    "x_capec_*"  # https://github.com/mitre-attack/attack-stix-data/issues/34
)
unsupported_ref_patterns = [MITRE_X_CAPEC]


class OpenCTIStix2Splitter:
    def __init__(self):
        self.cache_index = {}
        self.elements = []
        self.unsupported_patterns = list(
            map(lambda pattern: re.compile(pattern), unsupported_ref_patterns)
        )

    def is_ref_key_supported(self, key):
        for pattern in self.unsupported_patterns:
            if pattern.match(key):
                return False
        return True

    def enlist_element(self, item_id, raw_data):
        nb_deps = 1
        if item_id not in raw_data:
            return 0
        existing_item = self.cache_index.get(item_id)
        if existing_item is not None:
            return existing_item["nb_deps"]
        # Recursive enlist for every refs
        item = raw_data[item_id]
        for key in list(item.keys()):
            value = item[key]
            if key.endswith("_refs") and self.is_ref_key_supported(key):
                to_keep = []
                for element_ref in item[key]:
                    if element_ref != item_id:
                        nb_deps += self.enlist_element(element_ref, raw_data)
                        to_keep.append(element_ref)
                    item[key] = to_keep
            elif key.endswith("_ref") and self.is_ref_key_supported(key):
                if item[key] == item_id:
                    item[key] = None
                else:
                    # Need to handle the special case of recursive ref for created by ref
                    is_created_by_ref = key == "created_by_ref"
                    if is_created_by_ref:
                        is_marking = item["id"].startswith("marking-definition--")
                        if is_marking is False:
                            nb_deps += self.enlist_element(value, raw_data)
                    else:
                        nb_deps += self.enlist_element(value, raw_data)
        # Get the final dep counting and add in cache
        item["nb_deps"] = nb_deps
        self.elements.append(item)
        self.cache_index[item_id] = item  # Put in cache
        return nb_deps

    def split_bundle_with_expectations(
        self, bundle, use_json=True, event_version=None, relations_grouping=True
    ) -> Tuple[int, list]:
        """splits a valid stix2 bundle into a list of bundles"""
        if use_json:
            try:
                bundle_data = json.loads(bundle)
            except:
                raise Exception("File data is not a valid JSON")
        else:
            bundle_data = bundle

        if "objects" not in bundle_data:
            raise Exception("File data is not a valid bundle")
        if "id" not in bundle_data:
            bundle_data["id"] = "bundle--" + str(uuid.uuid4())

        raw_data = {}

        # Build flat list of elements
        for item in bundle_data["objects"]:
            raw_data[item["id"]] = item
        for item in bundle_data["objects"]:
            self.enlist_element(item["id"], raw_data)

        # Build the bundles
        bundles = []

        def by_dep_size(elem):
            return elem["nb_deps"]

        self.elements.sort(key=by_dep_size)

        # Algorithm to re-bundle elements
        # Bundle created group the relationships by dependencies
        # This grouping will improve relations sharding
        if relations_grouping:
            cache_ids = {}
            id_alias = {}
            ids_equivalence = {}
            working_elements = {}
            grouped_elements = {}
            for elem in self.elements:
                if cache_ids.get(elem["id"]):
                    # Prevent sending duplicate elements for ingest
                    continue
                nb_deps = elem["nb_deps"]
                if elem["type"] == "relationship":
                    source_ref = (
                        ids_equivalence.get(elem["source_ref"], elem["source_ref"])
                        + "-"
                        + str(nb_deps)
                    )
                    target_ref = (
                        ids_equivalence.get(elem["target_ref"], elem["target_ref"])
                        + "-"
                        + str(nb_deps)
                    )
                    target_source = id_alias.get(source_ref)
                    target_target = id_alias.get(target_ref)

                    target = "generated-" + str(uuid.uuid4())
                    if target_source is None and target_target is not None:
                        target = target_target
                        id_alias[source_ref] = target
                    if target_source is not None and target_target is None:
                        target = target_source
                        id_alias[target_ref] = target
                    if target_source is not None and target_target is not None:
                        target = target_target

                    if grouped_elements.get(target):
                        target_dict = grouped_elements.get(target, [])
                        target_dict["elements"].append(elem)
                        grouped_elements[target] = target_dict
                    else:
                        grouped_elements[target] = {
                            "nb_deps": nb_deps,
                            "elements": [elem],
                        }
                        id_alias[source_ref] = target
                        id_alias[target_ref] = target
                else:
                    work_id = elem["id"]
                    working_elements[work_id] = {"nb_deps": nb_deps, "elements": [elem]}
                cache_ids[elem["id"]] = elem["id"]
            split_elements = list(working_elements.values()) + list(
                grouped_elements.values()
            )
            split_elements.sort(key=by_dep_size)
        else:
            split_elements = list(
                map(lambda e: {"nb_deps": e["nb_deps"], "elements": [e]}, self.elements)
            )

        number_expectations = 0
        for entity in split_elements:
            number_expectations += len(entity["elements"])
            bundles.append(
                self.stix2_create_bundle(
                    bundle_data["id"],
                    entity["nb_deps"],
                    entity["elements"],
                    use_json,
                    event_version,
                )
            )

        return number_expectations, bundles

    @deprecated("Use split_bundle_with_expectations instead")
    def split_bundle(
        self, bundle, use_json=True, event_version=None, relations_grouping=True
    ) -> list:
        expectations, bundles = self.split_bundle_with_expectations(
            bundle, use_json, event_version, relations_grouping
        )
        return bundles

    @staticmethod
    def stix2_create_bundle(bundle_id, bundle_seq, items, use_json, event_version=None):
        """create a stix2 bundle with items

        :param items: valid stix2 items
        :type items:
        :param use_json: use JSON?
        :type use_json:
        :return: JSON of the stix2 bundle
        :rtype:
        """

        bundle = {
            "type": "bundle",
            "id": bundle_id,
            "spec_version": "2.1",
            "x_opencti_seq": bundle_seq,
            "objects": items,
        }
        if event_version is not None:
            bundle["x_opencti_event_version"] = event_version
        return json.dumps(bundle) if use_json else bundle
