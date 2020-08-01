# coding: utf-8

import json
from pycti.utils.opencti_stix2 import SPEC_VERSION


class StixCyberObservable:
    def __init__(self, opencti):
        self.opencti = opencti
        self.properties = """
            id
            stix_id
            entity_type
            name
            description
            observable_value
            created_at
            updated_at
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
            labels {
                edges {
                    node {
                        id
                        label_type
                        value
                        color
                    }
                    relation {
                        id
                    }
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
            indicators {
                edges {
                    node {
                        id
                        entity_type
                        stix_id
                        valid_from
                        valid_until
                        score
                        pattern_type
                        indicator_pattern
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
        List StixCyberObservable objects

        :param types: the array of types
        :param filters: the filters to apply
        :param search: the search keyword
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row
        :return List of StixCyberObservable objects
    """

    def list(self, **kwargs):
        types = kwargs.get("types", None)
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
            "info",
            "Listing StixCyberObservables with filters " + json.dumps(filters) + ".",
        )
        query = (
            """
            query StixCyberObservables($types: [String], $filters: [StixCyberObservablesFiltering], $search: String, $first: Int, $after: ID, $orderBy: StixCyberObservablesOrdering, $orderMode: OrderingMode) {
                StixCyberObservables(types: $types, filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
                "types": types,
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
            data = self.opencti.process_multiple(result["data"]["StixCyberObservables"])
            final_data = final_data + data
            while result["data"]["StixCyberObservables"]["pageInfo"]["hasNextPage"]:
                after = result["data"]["StixCyberObservables"]["pageInfo"]["endCursor"]
                self.opencti.log("info", "Listing StixCyberObservables after " + after)
                result = self.opencti.query(
                    query,
                    {
                        "types": types,
                        "filters": filters,
                        "search": search,
                        "first": first,
                        "after": after,
                        "orderBy": order_by,
                        "orderMode": order_mode,
                    },
                )
                data = self.opencti.process_multiple(
                    result["data"]["StixCyberObservables"]
                )
                final_data = final_data + data
            return final_data
        else:
            return self.opencti.process_multiple(
                result["data"]["StixCyberObservables"], with_pagination
            )

    """
        Read a StixCyberObservable object

        :param id: the id of the StixCyberObservable
        :param filters: the filters to apply if no id provided
        :return StixCyberObservable object
    """

    def read(self, **kwargs):
        id = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self.opencti.log("info", "Reading StixCyberObservable {" + id + "}.")
            query = (
                """
                query StixCyberObservable($id: String!) {
                    StixCyberObservable(id: $id) {
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
                result["data"]["StixCyberObservable"]
            )
        elif filters is not None:
            result = self.list(filters=filters, customAttributes=custom_attributes)
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self.opencti.log(
                "error",
                "[opencti_stix_cyber_observable] Missing parameters: id or filters",
            )
            return None

    """
        Create a Stix-Observable object

        :param type: the type of the Observable
        :return Stix-Observable object
    """

    def create_raw(self, **kwargs):
        type = kwargs.get("type", None)
        observable_value = kwargs.get("observable_value", None)
        description = kwargs.get("description", None)
        id = kwargs.get("id", None)
        stix_id = kwargs.get("stix_id", None)
        created_by = kwargs.get("createdBy", None)
        object_marking = kwargs.get("objectMarking", None)
        object_label = kwargs.get("objectLabel", None)
        create_indicator = kwargs.get("createIndicator", False)

        if type is not None and observable_value is not None:
            self.opencti.log(
                "info",
                "Creating Stix-Observable {"
                + observable_value
                + "} with indicator at "
                + str(create_indicator)
                + ".",
            )
            query = """
                mutation StixCyberObservableAdd($input: StixCyberObservableAddInput) {
                    StixCyberObservableAdd(input: $input) {
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
                        "type": type,
                        "observable_value": observable_value,
                        "description": description,
                        "internal_id_key": id,
                        "stix_id": stix_id,
                        "createdBy": created_by,
                        "objectMarking": objectMarking,
                        "labels": labels,
                        "createIndicator": create_indicator,
                    }
                },
            )
            return self.opencti.process_multiple_fields(
                result["data"]["StixCyberObservableAdd"]
            )
        else:
            self.opencti.log("error", "Missing parameters: type and observable_value")

    """
        Create a Stix-Observable object only if it not exists, update it on request

        :param name: the name of the Stix-Observable
        :return Stix-Observable object
    """

    def create(self, **kwargs):
        type = kwargs.get("type", None)
        observable_value = kwargs.get("observable_value", None)
        description = kwargs.get("description", None)
        id = kwargs.get("id", None)
        stix_id = kwargs.get("stix_id", None)
        created_by = kwargs.get("createdBy", None)
        object_marking = kwargs.get("objectMarking", None)
        object_label = kwargs.get("objectLabel", None)
        create_indicator = kwargs.get("createIndicator", False)
        update = kwargs.get("update", False)
        custom_attributes = """
            id
            entity_type
            description
            createdBy {
                node {
                    id
                }
            }            
        """
        object_result = self.read(
            filters=[{"key": "observable_value", "values": [observable_value]}],
            customAttributes=custom_attributes,
        )
        if object_result is not None:
            if update or object_result["createdById"] == created_by:
                if (
                    description is not None
                    and object_result["description"] != "description"
                ):
                    self.update_field(
                        id=object_result["id"], key="description", value=description
                    )
                    object_result["description"] = description
            return object_result
        else:
            return self.create_raw(
                type=type,
                observable_value=observable_value,
                description=description,
                id=id,
                stix_id=stix_id,
                createdBy=created_by,
                objectMarking=object_marking,
                objectLabel=object_label,
                createIndicator=create_indicator,
            )

    """
        Update a Stix-Observable object field

        :param id: the Stix-Observable id
        :param key: the key of the field
        :param value: the value of the field
        :return The updated Stix-Observable object
    """

    def update_field(self, **kwargs):
        id = kwargs.get("id", None)
        key = kwargs.get("key", None)
        value = kwargs.get("value", None)
        if id is not None and key is not None and value is not None:
            self.opencti.log(
                "info", "Updating Stix-Observable {" + id + "} field {" + key + "}."
            )
            query = """
                mutation StixCyberObservableEdit($id: ID!, $input: EditInput!) {
                    StixCyberObservableEdit(id: $id) {
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
                result["data"]["StixCyberObservableEdit"]["fieldPatch"]
            )
        else:
            self.opencti.log(
                "error",
                "[opencti_stix_cyber_observable_update_field] Missing parameters: id and key and value",
            )
            return None

    """
        Delete a Stix-Observable

        :param id: the Stix-Observable id
        :return void
    """

    def delete(self, **kwargs):
        id = kwargs.get("id", None)
        if id is not None:
            self.opencti.log("info", "Deleting Stix-Observable {" + id + "}.")
            query = """
                 mutation StixCyberObservableEdit($id: ID!) {
                     StixCyberObservableEdit(id: $id) {
                         delete
                     }
                 }
             """
            self.opencti.query(query, {"id": id})
        else:
            self.opencti.log(
                "error", "[opencti_stix_cyber_observable_delete] Missing parameters: id"
            )
            return None

    """
        Update the Identity author of a Stix-Observable object (created_by)

        :param id: the id of the Stix-Observable
        :param identity_id: the id of the Identity
        :return Boolean
    """

    def update_created_by(self, **kwargs):
        id = kwargs.get("id", None)
        opencti_stix_object_or_stix_relationship = kwargs.get("entity", None)
        identity_id = kwargs.get("identity_id", None)
        if id is not None and identity_id is not None:
            if opencti_stix_object_or_stix_relationship is None:
                custom_attributes = """
                    id
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
                """
                opencti_stix_object_or_stix_relationship = self.read(
                    id=id, customAttributes=custom_attributes
                )
            if opencti_stix_object_or_stix_relationship is None:
                self.opencti.log("error", "Cannot update created_by, entity not found")
                return False
            current_identity_id = None
            current_relation_id = None
            if opencti_stix_object_or_stix_relationship["createdBy"] is not None:
                current_identity_id = opencti_stix_object_or_stix_relationship[
                    "createdBy"
                ]["id"]
                current_relation_id = opencti_stix_object_or_stix_relationship[
                    "createdBy"
                ]["remote_relation_id"]
            # Current identity is the same
            if current_identity_id == identity_id:
                return True
            else:
                self.opencti.log(
                    "info",
                    "Updating author of Stix-Entity {"
                    + id
                    + "} with Identity {"
                    + identity_id
                    + "}",
                )
                # Current identity is different, delete the old relation
                if current_relation_id is not None:
                    query = """
                        mutation StixCyberObservableEdit($id: ID!, $relationId: ID!) {
                            StixCyberObservableEdit(id: $id) {
                                relationDelete(relationId: $relationId) {
                                    id
                                }
                            }
                        }
                    """
                    self.opencti.query(
                        query, {"id": id, "relationId": current_relation_id}
                    )
                # Add the new relation
                query = """
                   mutation StixCyberObservableEdit($id: ID!, $input: StixMetaRelationshipAddInput) {
                       StixCyberObservableEdit(id: $id) {
                            relationAdd(input: $input) {
                                id
                            }
                       }
                   }
                """
                variables = {
                    "id": id,
                    "input": {
                        "fromRole": "so",
                        "toId": identity_id,
                        "toRole": "creator",
                        "through": "created_by",
                    },
                }
                self.opencti.query(query, variables)

        else:
            self.opencti.log("error", "Missing parameters: id and identity_id")
            return False

    """
        Export an Stix Observable object in STIX2

        :param id: the id of the Stix Observable
        :return Stix Observable object
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
            stix_observable = dict()
            stix_observable["id"] = entity["stix_id"]
            stix_observable["type"] = entity["entity_type"]
            stix_observable["spec_version"] = SPEC_VERSION
            stix_observable["value"] = entity["observable_value"]
            stix_observable[CustomProperties.OBSERVABLE_TYPE] = entity["entity_type"]
            stix_observable[CustomProperties.OBSERVABLE_VALUE] = entity[
                "observable_value"
            ]
            stix_observable["created"] = self.opencti.stix2.format_date(
                entity["created_at"]
            )
            stix_observable["modified"] = self.opencti.stix2.format_date(
                entity["updated_at"]
            )
            stix_observable[CustomProperties.ID] = entity["id"]
            return self.opencti.stix2.prepare_export(
                entity, stix_observable, mode, max_marking_definition_entity
            )
        else:
            self.opencti.log("error", "Missing parameters: id or entity")
