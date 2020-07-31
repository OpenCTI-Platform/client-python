# coding: utf-8

import json
from pycti.utils.constants import CustomProperties
from pycti.utils.opencti_stix2 import SPEC_VERSION


class AttackPattern:
    def __init__(self, opencti):
        self.opencti = opencti
        self.properties = """
            id
            standard_id
            entity_type
            parent_types
            spec_version
            created_at
            updated_at
            createdBy {
                ... on Identity {
                    id
                    standard_id
                    entity_type
                    parent_types
                    name
                    aliases
                    description
                    created
                    modified
                }
                ... on Organization {
                    x_opencti_organization_type
                    x_opencti_reliability
                }
                ... on Individual {
                    x_opencti_firstname
                    x_opencti_lastname
                }
            }
            objectMarking {
                edges {
                    node {
                        id
                        standard_id
                        entity_type
                        definition_type
                        definition
                        created
                        modified
                        x_opencti_order
                        x_opencti_color
                    }
                }
            }
            objectLabel {
                edges {
                    node {
                        id
                        value
                        color
                    }
                }
            }
            externalReferences {
                edges {
                    node {
                        id
                        standard_id
                        entity_type
                        source_name
                        description
                        url
                        hash
                        external_id
                        created
                        modified
                    }
                }
            }
            revoked
            confidence
            created
            modified
            name
            description
            aliases
            x_mitre_platforms
            x_mitre_permissions_required
            x_mitre_detection
            x_mitre_id
            killChainPhases {
                edges {
                    node {
                        id
                        standard_id                            
                        entity_type
                        kill_chain_name
                        phase_name
                        x_opencti_order
                        created
                        modified
                    }
                }
            }        
        """

    """
        List Attack-Pattern objects

        :param filters: the filters to apply
        :param search: the search keyword
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of Attack-Pattern objects
    """

    def list(self, **kwargs):
        filters = kwargs.get("filters", None)
        search = kwargs.get("search", None)
        first = kwargs.get("first", 500)
        after = kwargs.get("after", None)
        order_by = kwargs.get("orderBy", None)
        order_mode = kwargs.get("orderMode", None)
        custom_attributes = kwargs.get("customAttributes", None)
        get_all = kwargs.get("getAll", False)
        with_pagination = kwargs.get("withPagination", False)
        if get_all:
            first = 500

        self.opencti.log(
            "info", "Listing Attack-Patterns with filters " + json.dumps(filters) + "."
        )
        query = (
            """
            query AttackPatterns($filters: [AttackPatternsFiltering], $search: String, $first: Int, $after: ID, $orderBy: AttackPatternsOrdering, $orderMode: OrderingMode) {
                attackPatterns(filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
                    edges {
                        node {
                            """
            + (custom_attributes if custom_attributes is not None else self.properties)
            + """
                        }
                    }
                    pageInfo {
                        startCursor
                        endCursor
                        hasNextPage
                        hasPreviousPage
                        globalCount
                    }
                }
            }
        """
        )
        result = self.opencti.query(
            query,
            {
                "filters": filters,
                "search": search,
                "first": first,
                "after": after,
                "orderBy": order_by,
                "orderMode": order_mode,
            },
        )
        if get_all:
            final_data = []
            data = self.opencti.process_multiple(result["data"]["attackPatterns"])
            final_data = final_data + data
            while result["data"]["attackPatterns"]["pageInfo"]["hasNextPage"]:
                after = result["data"]["attackPatterns"]["pageInfo"]["endCursor"]
                self.opencti.log("info", "Listing Attack-Patterns after " + after)
                result = self.opencti.query(
                    query,
                    {
                        "filters": filters,
                        "search": search,
                        "first": first,
                        "after": after,
                        "orderBy": order_by,
                        "orderMode": order_mode,
                    },
                )
                data = self.opencti.process_multiple(result["data"]["attackPatterns"])
                final_data = final_data + data
            return final_data
        else:
            return self.opencti.process_multiple(
                result["data"]["attackPatterns"], with_pagination
            )

    """
        Read a Attack-Pattern object
        
        :param id: the id of the Attack-Pattern
        :param filters: the filters to apply if no id provided
        :return Attack-Pattern object
    """

    def read(self, **kwargs):
        id = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self.opencti.log("info", "Reading Attack-Pattern {" + id + "}.")
            query = (
                """
                query AttackPattern($id: String!) {
                    attackPattern(id: $id) {
                        """
                + (
                    custom_attributes
                    if custom_attributes is not None
                    else self.properties
                )
                + """
                    }
                }
             """
            )
            result = self.opencti.query(query, {"id": id})
            return self.opencti.process_multiple_fields(result["data"]["attackPattern"])
        elif filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self.opencti.log(
                "error", "[opencti_attack_pattern] Missing parameters: id or filters"
            )
            return None

    """
        Create a Attack-Pattern object

        :param name: the name of the Attack Pattern
        :return Attack-Pattern object
    """

    def create_raw(self, **kwargs):
        stix_id = kwargs.get("stix_id", None)
        created_by = kwargs.get("createdBy", None)
        object_marking = kwargs.get("objectMarking", None)
        object_label = kwargs.get("objectLabel", None)
        external_references = kwargs.get("externalReferences", None)
        revoked = kwargs.get("revoked", None)
        confidence = kwargs.get("confidence", None)
        lang = kwargs.get("lang", None)
        created = kwargs.get("created", None)
        modified = kwargs.get("modified", None)
        name = kwargs.get("name", None)
        description = kwargs.get("description", "")
        aliases = kwargs.get("aliases", None)
        x_mitre_platforms = kwargs.get("x_mitre_platforms", None)
        x_mitre_permissions_required = kwargs.get("x_mitre_permissions_required", None)
        x_mitre_detection = kwargs.get("x_mitre_detection", None)
        x_mitre_id = kwargs.get("x_mitre_id", None)
        kill_chain_phases = kwargs.get("killChainPhases", None)

        if name is not None and description is not None:
            self.opencti.log("info", "Creating Attack-Pattern {" + name + "}.")
            query = """
                mutation AttackPatternAdd($input: AttackPatternAddInput) {
                    attackPatternAdd(input: $input) {
                        id
                        standard_id
                        entity_type
                        parent_types
                    }
                }
            """
            result = self.opencti.query(
                query,
                {
                    "input": {
                        "stix_id": stix_id,
                        "createdBy": created_by,
                        "objectMarking": object_marking,
                        "objectLabel": object_label,
                        "externalReferences": external_references,
                        "revoked": revoked,
                        "confidence": confidence,
                        "lang": lang,
                        "created": created,
                        "modified": modified,
                        "name": name,
                        "description": description,
                        "aliases": aliases,
                        "x_mitre_platforms": x_mitre_platforms,
                        "x_mitre_permissions_required": x_mitre_permissions_required,
                        "x_mitre_detection": x_mitre_detection,
                        "x_mitre_id": x_mitre_id,
                        "killChainPhases": kill_chain_phases,
                    }
                },
            )
            return self.opencti.process_multiple_fields(
                result["data"]["attackPatternAdd"]
            )
        else:
            self.opencti.log(
                "error",
                "[opencti_attack_pattern] Missing parameters: name and description",
            )

    """
        Create a Attack-Pattern object only if it not exists, update it on request

        :param name: the name of the Attack-Pattern
        :return Attack-Pattern object
    """

    def create(self, **kwargs):
        stix_id = kwargs.get("stix_id", None)
        created_by = kwargs.get("createdBy", None)
        object_marking = kwargs.get("objectMarking", None)
        object_label = kwargs.get("objectLabel", None)
        external_references = kwargs.get("externalReferences", None)
        revoked = kwargs.get("revoked", None)
        confidence = kwargs.get("confidence", None)
        lang = kwargs.get("lang", None)
        created = kwargs.get("created", None)
        modified = kwargs.get("modified", None)
        name = kwargs.get("name", None)
        description = kwargs.get("description", "")
        aliases = kwargs.get("aliases", None)
        x_mitre_platforms = kwargs.get("x_mitre_platforms", None)
        x_mitre_permissions_required = kwargs.get("x_mitre_permissions_required", None)
        x_mitre_detection = kwargs.get("x_mitre_detection", None)
        x_mitre_id = kwargs.get("x_mitre_id", None)
        kill_chain_phases = kwargs.get("killChainPhases", None)
        update = kwargs.get("update", False)
        custom_attributes = """
            id
            standard_id
            entity_type
            parent_types
            createdBy {
                ... on Identity {
                    id
                }
            }
            name
            description
            aliases
            x_mitre_platforms
            x_mitre_permissions_required
            x_mitre_detection
            x_mitre_id
            killChainPhases {
                edges {
                    node {
                        id
                        standard_id                            
                        entity_type
                        kill_chain_name
                        phase_name
                        x_opencti_order
                        created
                        modified
                    }
                }
            }
        """
        object_result = None
        if stix_id is not None:
            object_result = self.read(id=stix_id, customAttributes=custom_attributes)
        if object_result is None and x_mitre_id is not None:
            object_result = self.read(
                filters=[
                    {"key": "x_mitre_id", "values": [x_mitre_id], "operator": "match"}
                ]
            )
        if object_result is None and name is not None:
            object_result = self.read(
                filters=[{"key": "name", "values": [name]}],
                customAttributes=custom_attributes,
            )
            if object_result is None:
                object_result = self.read(
                    filters=[{"key": "aliases", "values": [name]}],
                    customAttributes=custom_attributes,
                )
            # If x_mitre_id mismatch, no duplicate
            if object_result is not None:
                if object_result["x_mitre_id"] is not None and x_mitre_id is not None:
                    if object_result["x_mitre_id"] != x_mitre_id:
                        object_result = None
        if object_result is not None:
            if update or object_result["createdById"] == created_by:
                # name
                if object_result["name"] != name:
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="name", value=name
                    )
                    object_result["name"] = name
                # description
                if (
                    self.opencti.not_empty(description)
                    and object_result["description"] != description
                ):
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="description", value=description
                    )
                    object_result["description"] = description
                # aliases
                if (
                    self.opencti.not_empty(aliases)
                    and object_result["aliases"] != aliases
                ):
                    if "aliases" in object_result:
                        new_aliases = object_result["aliases"] + list(
                            set(aliases) - set(object_result["aliases"])
                        )
                    else:
                        new_aliases = aliases
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="aliases", value=new_aliases
                    )
                    object_result["aliases"] = new_aliases
                # x_mitre_platforms
                if (
                    self.opencti.not_empty(x_mitre_platforms)
                    and object_result["x_mitre_platforms"] != x_mitre_platforms
                ):
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"],
                        key="x_mitre_platforms",
                        value=x_mitre_platforms,
                    )
                    object_result["x_mitre_platforms"] = x_mitre_platforms
                # x_mitre_permissions_required
                if (
                    self.opencti.not_empty(x_mitre_permissions_required)
                    and object_result["x_mitre_permissions_required"]
                    != x_mitre_permissions_required
                ):
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"],
                        key="x_mitre_permissions_required",
                        value=x_mitre_permissions_required,
                    )
                    object_result[
                        "x_mitre_permissions_required"
                    ] = x_mitre_permissions_required
                # x_mitre_id
                if (
                    self.opencti.not_empty(x_mitre_id)
                    and object_result["x_mitre_id"] != x_mitre_id
                ):
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="x_mitre_id", value=str(x_mitre_id),
                    )
                    object_result["x_mitre_id"] = x_mitre_id
                # confidence
                if (
                    self.opencti.not_empty(confidence)
                    and object_result["confidence"] != confidence
                ):
                    self.opencti.stix_domain_object.update_field(
                        id=object_result["id"], key="confidence", value=str(confidence)
                    )
                    object_result["confidence"] = confidence
            return object_result
        else:
            return self.create_raw(
                stix_id=stix_id,
                createdBy=created_by,
                objectMarking=object_marking,
                objectLabel=object_label,
                externalReferences=external_references,
                revoked=revoked,
                confidence=confidence,
                lang=lang,
                created=created,
                modified=modified,
                name=name,
                description=description,
                aliases=aliases,
                x_mitre_platforms=x_mitre_platforms,
                x_mitre_permissions_required=x_mitre_permissions_required,
                x_mitre_detection=x_mitre_detection,
                x_mitre_id=x_mitre_id,
                killChainPhases=kill_chain_phases,
            )

    """
        Import an Attack-Pattern object from a STIX2 object

        :param stixObject: the Stix-Object Attack-Pattern
        :return Attack-Pattern object
    """

    def import_from_stix2(self, **kwargs):
        stix_object = kwargs.get("stixObject", None)
        extras = kwargs.get("extras", {})
        update = kwargs.get("update", False)
        if stix_object is not None:
            # Extract external ID
            x_mitre_id = None
            if "x_mitre_id" in stix_object:
                x_mitre_id = stix_object["x_mitre_id"]
            if "external_references" in stix_object:
                for external_reference in stix_object["external_references"]:
                    if (
                        external_reference["source_name"] == "mitre-attack"
                        or external_reference["source_name"] == "mitre-pre-attack"
                        or external_reference["source_name"] == "mitre-mobile-attack"
                        or external_reference["source_name"] == "amitt-attack"
                    ):
                        x_mitre_id = external_reference["external_id"]
            return self.create(
                stix_id=stix_object["id"],
                createdBy=extras["created_by_id"]
                if "created_by_id" in extras
                else None,
                objectMarking=extras["object_marking_ids"]
                if "object_marking_ids" in extras
                else None,
                objectLabel=extras["object_label_ids"]
                if "object_label_ids" in extras
                else [],
                externalReferences=extras["external_references_ids"]
                if "external_references_ids" in extras
                else [],
                revoked=stix_object["revoked"] if "revoked" in stix_object else None,
                confidence=stix_object["confidence"]
                if "confidence" in stix_object
                else None,
                lang=stix_object["lang"] if "lang" in stix_object else None,
                created=stix_object["created"] if "created" in stix_object else None,
                modified=stix_object["modified"] if "modified" in stix_object else None,
                name=stix_object["name"],
                description=self.opencti.stix2.convert_markdown(
                    stix_object["description"]
                )
                if "description" in stix_object
                else "",
                aliases=self.opencti.stix2.pick_aliases(stix_object),
                x_mitre_platforms=stix_object["x_mitre_platforms"]
                if "x_mitre_platforms" in stix_object
                else stix_object["x_amitt_platforms"]
                if "x_amitt_platforms" in stix_object
                else None,
                x_mitre_permissions_required=stix_object["x_mitre_permissions_required"]
                if "x_mitre_permissions_required" in stix_object
                else None,
                x_mitre_detection=stix_object["x_mitre_detection"]
                if "x_mitre_detection" in stix_object
                else None,
                x_mitre_id=x_mitre_id,
                killChainPhases=extras["kill_chain_phases_ids"]
                if "kill_chain_phases_ids" in extras
                else None,
                update=update,
            )
        else:
            self.opencti.log(
                "error", "[opencti_attack_pattern] Missing parameters: stixObject"
            )

    """
        Export an Attack-Pattern object in STIX2
    
        :param id: the id of the Attack-Pattern
        :return Attack-Pattern object
    """

    def to_stix2(self, **kwargs):
        id = kwargs.get("id", None)
        mode = kwargs.get("mode", "simple")
        max_marking_definition_entity = kwargs.get(
            "max_marking_definition_entity", None
        )
        entity = kwargs.get("entity", None)
        if id is not None and entity is None:
            entity = self.read(id=id)
        if entity is not None:
            attack_pattern = dict()
            attack_pattern["id"] = entity["stix_id"]
            attack_pattern["type"] = "attack-pattern"
            attack_pattern["spec_version"] = entity["spec_version"]
            attack_pattern["name"] = entity["name"]
            if self.opencti.not_empty(entity["stix_label"]):
                attack_pattern["labels"] = entity["stix_label"]
            else:
                attack_pattern["labels"] = ["attack-pattern"]
            if self.opencti.not_empty(entity["description"]):
                attack_pattern["description"] = entity["description"]
            attack_pattern["created"] = self.opencti.stix2.format_date(
                entity["created"]
            )
            attack_pattern["modified"] = self.opencti.stix2.format_date(
                entity["modified"]
            )
            if self.opencti.not_empty(entity["platform"]):
                attack_pattern["x_mitre_platforms"] = entity["platform"]
            if self.opencti.not_empty(entity["required_permission"]):
                attack_pattern["x_mitre_permissions_required"] = entity[
                    "required_permission"
                ]
            if self.opencti.not_empty(entity["external_id"]):
                attack_pattern[CustomProperties.EXTERNAL_ID] = entity["external_id"]
            if self.opencti.not_empty(entity["alias"]):
                attack_pattern[CustomProperties.ALIASES] = entity["alias"]
            attack_pattern[CustomProperties.ID] = entity["id"]
            return self.opencti.stix2.prepare_export(
                entity, attack_pattern, mode, max_marking_definition_entity
            )
        else:
            self.opencti.log(
                "error", "[opencti_attack_pattern] Missing parameters: id or entity"
            )
