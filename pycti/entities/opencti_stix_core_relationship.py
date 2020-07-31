# coding: utf-8

import dateutil.parser
import datetime
from pycti.utils.constants import CustomProperties
from pycti.utils.opencti_stix2 import SPEC_VERSION


class StixCoreRelationship:
    def __init__(self, opencti):
        self.opencti = opencti
        self.properties = """
            id
            stix_id
            entity_type
            relationship_type
            description
            weight
            role_played
            start_time
            stop_time
            created
            modified
            created_at
            updated_at
            fromRole
            from {
                id
                stix_id
                entity_type
                ...on StixDomainEntity {
                    name
                    description
                }
            }
            toRole
            to {
                id
                stix_id
                entity_type
                ...on StixDomainEntity {
                    name
                    description
                }
            }
            createdBy {
                node {
                    id
                    entity_type
                    stix_id
                    stix_label
                    name
                    alias
                    description
                    created
                    modified
                    ... on Organization {
                        x_opencti_organization_type
                    }
                }
                relation {
                    id
                }
            }
            markingDefinitions {
                edges {
                    node {
                        id
                        entity_type
                        stix_id
                        definition_type
                        definition
                        level
                        color
                        created
                        modified
                    }
                    relation {
                       id
                    }
                }
            }
            killChainPhases {
                edges {
                    node {
                        id
                        entity_type
                        stix_id
                        kill_chain_name
                        phase_name
                        phase_order
                        created
                        modified
                    }
                    relation {
                       id
                    }
                }
            }
            externalReferences {
                edges {
                    node {
                        id
                        entity_type
                        stix_id
                        source_name
                        description
                        url
                        hash
                        external_id
                        created
                        modified
                    }
                    relation {
                        id
                    }
                }
            }
        """

    """
        List stix_core_relationship objects

        :param fromId: the id of the source entity of the relation
        :param toId: the id of the target entity of the relation
        :param relationType: the relation type
        :param startTimeStart: the start_time date start filter
        :param startTimeStop: the start_time date stop filter
        :param stopTimeStart: the stop_time date start filter
        :param stopTimeStop: the stop_time date stop filter
        :param inferred: includes inferred relations
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of stix_core_relationship objects
    """

    def list(self, **kwargs):
        from_id = kwargs.get("fromId", None)
        from_types = kwargs.get("fromTypes", None)
        to_id = kwargs.get("toId", None)
        to_types = kwargs.get("toTypes", None)
        relation_type = kwargs.get("relationType", None)
        start_time_start = kwargs.get("startTimeStart", None)
        start_time_stop = kwargs.get("startTimeStop", None)
        stop_time_start = kwargs.get("stopTimeStart", None)
        stop_time_stop = kwargs.get("stopTimeStop", None)
        filters = kwargs.get("filters", [])
        inferred = kwargs.get("inferred", None)
        first = kwargs.get("first", 500)
        after = kwargs.get("after", None)
        order_by = kwargs.get("orderBy", None)
        order_mode = kwargs.get("orderMode", None)
        get_all = kwargs.get("getAll", False)
        with_pagination = kwargs.get("withPagination", False)
        force_natural = kwargs.get("forceNatural", False)
        if get_all:
            first = 500

        self.opencti.log(
            "info",
            "Listing stix_core_relationships with {type: "
            + str(relation_type)
            + ", from_id: "
            + str(from_id)
            + ", to_id: "
            + str(to_id)
            + "}",
        )
        query = (
            """
                query StixCoreRelationships($fromId: String, $fromTypes: [String], $toId: String, $toTypes: [String], $relationType: String, $startTimeStart: DateTime, $startTimeStop: DateTime, $stopTimeStart: DateTime, $stopTimeStop: DateTime, $inferred: Boolean, $filters: [StixCoreRelationshipsFiltering], $first: Int, $after: ID, $orderBy: StixCoreRelationshipsOrdering, $orderMode: OrderingMode, $forceNatural: Boolean) {
                    stixCoreRelationships(fromId: $fromId, fromTypes: $fromTypes, toId: $toId, toTypes: $toTypes, relationType: $relationType, startTimeStart: $startTimeStart, startTimeStop: $startTimeStop, stopTimeStart: $stopTimeStart, stopTimeStop: $stopTimeStop, inferred: $inferred, filters: $filters, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode, forceNatural: $forceNatural) {
                        edges {
                            node {
                                """
            + self.properties
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
                "fromId": from_id,
                "fromTypes": from_types,
                "toId": to_id,
                "toTypes": to_types,
                "relationType": relation_type,
                "startTimeStart": start_time_start,
                "startTimeStop": start_time_stop,
                "stopTimeStart": stop_time_start,
                "stopTimeStop": stop_time_stop,
                "filters": filters,
                "inferred": inferred,
                "first": first,
                "after": after,
                "orderBy": order_by,
                "orderMode": order_mode,
                "forceNatural": force_natural,
            },
        )
        return self.opencti.process_multiple(
            result["data"]["stixCoreRelationships"], with_pagination
        )

    """
        Read a stix_core_relationship object

        :param id: the id of the stix_core_relationship
        :param fromId: the id of the source entity of the relation
        :param toId: the id of the target entity of the relation
        :param relationType: the relation type
        :param startTimeStart: the start_time date start filter
        :param startTimeStop: the start_time date stop filter
        :param stopTimeStart: the stop_time date start filter
        :param stopTimeStop: the stop_time date stop filter
        :param inferred: includes inferred relations
        :return stix_core_relationship object
    """

    def read(self, **kwargs):
        id = kwargs.get("id", None)
        from_id = kwargs.get("fromId", None)
        to_id = kwargs.get("toId", None)
        relation_type = kwargs.get("relationType", None)
        start_time_start = kwargs.get("startTimeStart", None)
        start_time_stop = kwargs.get("startTimeStop", None)
        stop_time_start = kwargs.get("stopTimeStart", None)
        stop_time_stop = kwargs.get("stopTimeStop", None)
        inferred = kwargs.get("inferred", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self.opencti.log("info", "Reading stix_core_relationship {" + id + "}.")
            query = (
                """
                    query StixCoreRelationship($id: String!) {
                        stixCoreRelationship(id: $id) {
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
            return self.opencti.process_multiple_fields(
                result["data"]["stixCoreRelationship"]
            )
        elif from_id is not None and to_id is not None:
            result = self.list(
                fromId=from_id,
                toId=to_id,
                relationType=relation_type,
                startTimeStart=start_time_start,
                startTimeStop=start_time_stop,
                stopTimeStart=stop_time_start,
                stopTimeStop=stop_time_stop,
                inferred=inferred,
            )
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self.opencti.log("error", "Missing parameters: id or from_id and to_id")
            return None

    """
        Create a stix_core_relationship object

        :param name: the name of the Attack Pattern
        :return stix_core_relationship object
    """

    def create_raw(self, **kwargs):
        from_id = kwargs.get("fromId", None)
        from_role = kwargs.get("fromRole", None)
        to_id = kwargs.get("toId", None)
        to_role = kwargs.get("toRole", None)
        relationship_type = kwargs.get("relationship_type", None)
        description = kwargs.get("description", None)
        role_played = kwargs.get("role_played", None)
        start_time = kwargs.get("start_time", None)
        stop_time = kwargs.get("stop_time", None)
        weight = kwargs.get("weight", None)
        id = kwargs.get("id", None)
        stix_id = kwargs.get("stix_id", None)
        created = kwargs.get("created", None)
        modified = kwargs.get("modified", None)
        created_by = kwargs.get("createdBy", None)
        object_marking = kwargs.get("objectMarking", None)
        kill_chain_phases = kwargs.get("killChainPhases", None)

        self.opencti.log(
            "info",
            "Creating stix_core_relationship {"
            + from_role
            + ": "
            + from_id
            + ", "
            + to_role
            + ": "
            + to_id
            + "}.",
        )
        query = """
                mutation StixCoreRelationshipAdd($input: StixStixMetaRelationshipAddInput!) {
                    stixCoreRelationshipAdd(input: $input) {
                        id
                        stix_id
                        entity_type
                        parent_types
                    }
                }
            """
        result = self.opencti.query(
            query,
            {
                "input": {
                    "fromId": from_id,
                    "fromRole": from_role,
                    "toId": to_id,
                    "toRole": to_role,
                    "relationship_type": relationship_type,
                    "description": description,
                    "role_played": role_played,
                    "start_time": start_time,
                    "stop_time": stop_time,
                    "weight": weight,
                    "internal_id_key": id,
                    "stix_id": stix_id,
                    "created": created,
                    "modified": modified,
                    "createdBy": created_by,
                    "objectMarking": objectMarking,
                    "killChainPhases": kill_chain_phases,
                }
            },
        )
        return self.opencti.process_multiple_fields(
            result["data"]["stixCoreRelationshipAdd"]
        )

    """
        Create a stix_core_relationship object only if it not exists, update it on request

        :param name: the name of the stix_core_relationship
        :return stix_core_relationship object
    """

    def create(self, **kwargs):
        from_id = kwargs.get("fromId", None)
        from_type = kwargs.get("fromType", None)
        to_type = kwargs.get("toType", None)
        to_id = kwargs.get("toId", None)
        relationship_type = kwargs.get("relationship_type", None)
        description = kwargs.get("description", None)
        role_played = kwargs.get("role_played", None)
        start_time = kwargs.get("start_time", None)
        stop_time = kwargs.get("stop_time", None)
        weight = kwargs.get("weight", None)
        id = kwargs.get("id", None)
        stix_id = kwargs.get("stix_id", None)
        created = kwargs.get("created", None)
        modified = kwargs.get("modified", None)
        created_by = kwargs.get("createdBy", None)
        object_marking = kwargs.get("objectMarking", None)
        kill_chain_phases = kwargs.get("killChainPhases", None)
        update = kwargs.get("update", False)
        ignore_dates = kwargs.get("ignore_dates", False)
        custom_attributes = """
            id
            entity_type
            name
            description
            weight
            start_time
            stop_time
            createdBy {
                node {
                    id
                }
            }            
        """
        stix_core_relationship_result = None
        if id is not None:
            stix_core_relationship_result = self.read(
                id=id, customAttributes=custom_attributes
            )
        if stix_core_relationship_result is None and stix_id is not None:
            stix_core_relationship_result = self.read(
                id=stix_id, customAttributes=custom_attributes
            )
        if stix_core_relationship_result is None:
            if (
                ignore_dates is False
                and start_time is not None
                and stop_time is not None
            ):
                start_time_parsed = dateutil.parser.parse(start_time)
                start_time_start = (
                    start_time_parsed + datetime.timedelta(days=-1)
                ).strftime("%Y-%m-%dT%H:%M:%S+00:00")
                start_time_stop = (
                    start_time_parsed + datetime.timedelta(days=1)
                ).strftime("%Y-%m-%dT%H:%M:%S+00:00")
                stop_time_parsed = dateutil.parser.parse(stop_time)
                stop_time_start = (
                    stop_time_parsed + datetime.timedelta(days=-1)
                ).strftime("%Y-%m-%dT%H:%M:%S+00:00")
                stop_time_stop = (
                    stop_time_parsed + datetime.timedelta(days=1)
                ).strftime("%Y-%m-%dT%H:%M:%S+00:00")
            else:
                start_time_start = None
                start_time_stop = None
                stop_time_start = None
                stop_time_stop = None
            stix_core_relationship_result = self.read(
                fromId=from_id,
                toId=to_id,
                relationType=relationship_type,
                startTimeStart=start_time_start,
                startTimeStop=start_time_stop,
                stopTimeStart=stop_time_start,
                stopTimeStop=stop_time_stop,
                customAttributes=custom_attributes,
            )
        if stix_core_relationship_result is not None:
            if update or stix_core_relationship_result["createdBy"] == created_by:
                if (
                    description is not None
                    and stix_core_relationship_result["description"] != description
                ):
                    self.update_field(
                        id=stix_core_relationship_result["id"],
                        key="description",
                        value=description,
                    )
                    stix_core_relationship_result["description"] = description
                if (
                    weight is not None
                    and stix_core_relationship_result["weight"] != weight
                ):
                    self.update_field(
                        id=stix_core_relationship_result["id"],
                        key="weight",
                        value=str(weight),
                    )
                    stix_core_relationship_result["weight"] = weight
                if start_time is not None:
                    new_start_time = dateutil.parser.parse(start_time)
                    old_start_time = dateutil.parser.parse(
                        stix_core_relationship_result["start_time"]
                    )
                    if new_start_time < old_start_time:
                        self.update_field(
                            id=stix_core_relationship_result["id"],
                            key="start_time",
                            value=start_time,
                        )
                        stix_core_relationship_result["start_time"] = start_time
                if stop_time is not None:
                    new_stop_time = dateutil.parser.parse(stop_time)
                    old_stop_time = dateutil.parser.parse(
                        stix_core_relationship_result["stop_time"]
                    )
                    if new_stop_time > old_stop_time:
                        self.update_field(
                            id=stix_core_relationship_result["id"],
                            key="stop_time",
                            value=stop_time,
                        )
                        stix_core_relationship_result["stop_time"] = stop_time
            return stix_core_relationship_result
        else:
            roles = self.opencti.resolve_role(relationship_type, from_type, to_type)
            if roles is not None:
                final_from_id = from_id
                final_to_id = to_id
            else:
                roles = self.opencti.resolve_role(relationship_type, to_type, from_type)
                if roles is not None:
                    final_from_id = to_id
                    final_to_id = from_id
                else:
                    self.opencti.log(
                        "error",
                        "Relation creation failed, cannot resolve roles: {"
                        + relationship_type
                        + ": "
                        + from_type
                        + ", "
                        + to_type
                        + "}",
                    )
                    return None

            return self.create_raw(
                fromId=final_from_id,
                fromRole=roles["from_role"],
                toId=final_to_id,
                toRole=roles["to_role"],
                relationship_type=relationship_type,
                description=description,
                start_time=start_time,
                stop_time=stop_time,
                weight=weight,
                role_played=role_played,
                id=id,
                stix_id=stix_id,
                created=created,
                modified=modified,
                createdBy=created_by,
                objectMarking=object_marking,
                killChainPhases=kill_chain_phases,
            )

    """
        Update a stix_core_relationship object field

        :param id: the stix_core_relationship id
        :param key: the key of the field
        :param value: the value of the field
        :return The updated stix_core_relationship object
    """

    def update_field(self, **kwargs):
        id = kwargs.get("id", None)
        key = kwargs.get("key", None)
        value = kwargs.get("value", None)
        if id is not None and key is not None and value is not None:
            self.opencti.log(
                "info",
                "Updating stix_core_relationship {" + id + "} field {" + key + "}.",
            )
            query = """
                    mutation StixCoreRelationshipEdit($id: ID!, $input: EditInput!) {
                        stixCoreRelationshipEdit(id: $id) {
                            fieldPatch(input: $input) {
                                id
                            }
                        }
                    }
                """
            result = self.opencti.query(
                query, {"id": id, "input": {"key": key, "value": value}}
            )
            return self.opencti.process_multiple_fields(
                result["data"]["stixCoreRelationshipEdit"]["fieldPatch"]
            )
        else:
            self.opencti.log(
                "error",
                "[opencti_stix_core_relationship] Missing parameters: id and key and value",
            )
            return None

    """
        Delete a stix_core_relationship

        :param id: the stix_core_relationship id
        :return void
    """

    def delete(self, **kwargs):
        id = kwargs.get("id", None)
        if id is not None:
            self.opencti.log("info", "Deleting stix_core_relationship {" + id + "}.")
            query = """
                mutation StixCoreRelationshipEdit($id: ID!) {
                    stixCoreRelationshipEdit(id: $id) {
                        delete
                    }
                }
            """
            self.opencti.query(query, {"id": id})
        else:
            self.opencti.log(
                "error", "[opencti_stix_core_relationship] Missing parameters: id"
            )
            return None

    """
        Add a Kill-Chain-Phase object to stix_core_relationship object (kill_chain_phases)

        :param id: the id of the stix_core_relationship
        :param kill_chain_phase_id: the id of the Kill-Chain-Phase
        :return Boolean
    """

    def add_kill_chain_phase(self, **kwargs):
        id = kwargs.get("id", None)
        kill_chain_phase_id = kwargs.get("kill_chain_phase_id", None)
        if id is not None and kill_chain_phase_id is not None:
            opencti_stix_object_or_stix_core_relationshipship = self.read(id=id)
            kill_chain_phases_ids = []
            for marking in opencti_stix_object_or_stix_core_relationshipship[
                "killChainPhases"
            ]:
                kill_chain_phases_ids.append(marking["id"])
            if kill_chain_phase_id in kill_chain_phases_ids:
                return True
            else:
                self.opencti.log(
                    "info",
                    "Adding Kill-Chain-Phase {"
                    + kill_chain_phase_id
                    + "} to Stix-Entity {"
                    + id
                    + "}",
                )
                query = """
                   mutation StixCoreRelationshipAddRelation($id: ID!, $input: StixMetaRelationshipAddInput) {
                       stixCoreRelationshipEdit(id: $id) {
                            relationAdd(input: $input) {
                                id
                            }
                       }
                   }
                """
                self.opencti.query(
                    query,
                    {
                        "id": id,
                        "input": {
                            "fromRole": "phase_belonging",
                            "toId": kill_chain_phase_id,
                            "toRole": "kill_chain_phase",
                            "through": "kill_chain_phases",
                        },
                    },
                )
                return True
        else:
            self.opencti.log(
                "error",
                "[opencti_stix_core_relationship] Missing parameters: id and kill_chain_phase_id",
            )
            return False

    """
        Export an stix_core_relationship object in STIX2

        :param id: the id of the stix_core_relationship
        :return stix_core_relationship object
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
            roles = self.opencti.resolve_role(
                entity["relationship_type"],
                entity["from"]["entity_type"],
                entity["to"]["entity_type"],
            )
            if roles is not None:
                final_from_id = entity["from"]["stix_id"]
                final_to_id = entity["to"]["stix_id"]
            else:
                roles = self.opencti.resolve_role(
                    entity["relationship_type"],
                    entity["to"]["entity_type"],
                    entity["from"]["entity_type"],
                )
                if roles is not None:
                    final_from_id = entity["to"]["stix_id"]
                    final_to_id = entity["from"]["stix_id"]

            stix_core_relationship = dict()
            stix_core_relationship["id"] = entity["stix_id"]
            stix_core_relationship["type"] = "relationship"
            stix_core_relationship["spec_version"] = SPEC_VERSION
            stix_core_relationship["relationship_type"] = entity["relationship_type"]
            if self.opencti.not_empty(entity["description"]):
                stix_core_relationship["description"] = entity["description"]
            stix_core_relationship["source_ref"] = final_from_id
            stix_core_relationship["target_ref"] = final_to_id
            stix_core_relationship[CustomProperties.SOURCE_REF] = final_from_id
            stix_core_relationship[CustomProperties.TARGET_REF] = final_to_id
            stix_core_relationship["created"] = self.opencti.stix2.format_date(
                entity["created"]
            )
            stix_core_relationship["modified"] = self.opencti.stix2.format_date(
                entity["modified"]
            )
            if self.opencti.not_empty(entity["start_time"]):
                stix_core_relationship[
                    CustomProperties.FIRST_SEEN
                ] = self.opencti.stix2.format_date(entity["start_time"])
            if self.opencti.not_empty(entity["stop_time"]):
                stix_core_relationship[
                    CustomProperties.LAST_SEEN
                ] = self.opencti.stix2.format_date(entity["stop_time"])
            if self.opencti.not_empty(entity["weight"]):
                stix_core_relationship[CustomProperties.WEIGHT] = entity["weight"]
            if self.opencti.not_empty(entity["role_played"]):
                stix_core_relationship[CustomProperties.ROLE_PLAYED] = entity[
                    "role_played"
                ]
            stix_core_relationship[CustomProperties.ID] = entity["id"]
            return self.opencti.stix2.prepare_export(
                entity, stix_core_relationship, mode, max_marking_definition_entity
            )
        else:
            self.opencti.log(
                "error",
                "[opencti_stix_core_relationship] Missing parameters: id or entity",
            )
