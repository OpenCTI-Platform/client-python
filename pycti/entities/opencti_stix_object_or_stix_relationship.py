# coding: utf-8


class StixObjectOrStixRelationship:
    def __init__(self, opencti):
        self.opencti = opencti
        self.properties = """
            ... on StixObject {
                id
                standard_id
                entity_type
                parent_types
                spec_version
                created_at
                updated_at
            }
            ... on StixDomainObject {
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
            }
            ... on AttackPattern {
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
            }
            ... on Campaign {
                name
                description
                aliases
                first_seen
                last_seen
                objective
            }
            ... on Note {
                attribute_abstract
                content
                authors
            }
            ... on ObservedData {
                first_observed
                last_observed
                number_observed
            }
            ... on Opinion {
                explanation
                authors
                opinion
            }
            ... on Report {
                name
                description
                report_types
                published
                x_opencti_report_status
            }
            ... on CourseOfAction {
                name
                description
                x_opencti_aliases
            }
            ... on Individual {
                name
                description
                aliases
                contact_information
                x_opencti_firstname
                x_opencti_lastname
            }
            ... on Organization {
                name
                description
                aliases
                contact_information
                x_opencti_organization_type
                x_opencti_reliability
            }
            ... on Sector {
                name
                description
                aliases
                contact_information
            }
            ... on Indicator {
                pattern_type
                pattern_version
                pattern
                name
                description
                indicator_types
                valid_from
                valid_until
                x_opencti_score
                x_opencti_detection
                x_opencti_main_observable_type
            }
            ... on Infrastructure {
                name
                description
                aliases
                infrastructure_types
                first_seen
                last_seen
            }
            ... on IntrusionSet {
                name
                description
                aliases
                first_seen
                last_seen
                goals
                resource_level
                primary_motivation
                secondary_motivations
            }
            ... on City {
                name
                description
                latitude
                longitude
                precision
                x_opencti_aliases
            }
            ... on Country {
                name
                description
                latitude
                longitude
                precision
                x_opencti_aliases
            }
            ... on  Region {
                name
                description
                latitude
                longitude
                precision
                x_opencti_aliases
            }
            ... on Position {
                name
                description
                latitude
                longitude
                precision
                x_opencti_aliases
                street_address
                postal_code
            }
            ... on Malware {
                name
                description
                aliases
                malware_types
                is_family
                first_seen
                last_seen
                architecture_execution_envs
                implementation_languages
                capabilities
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
            }
            ... on ThreatActor {
                name
                description
                aliases
                threat_actor_types
                first_seen
                last_seen
                roles
                goals
                sophistication
                resource_level
                primary_motivation
                secondary_motivations
                personal_motivations
            }
            ... on Tool {
                name
                description
                aliases
                tool_types
                tool_version
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
            }
            ... on Vulnerability {
                name
                description
                x_opencti_base_score
                x_opencti_base_severity
                x_opencti_attack_vector
                x_opencti_integrity_impact
                x_opencti_availability_impact
            }
            ... on XOpenctiIncident {
                name
                description
                aliases
                first_seen
                last_seen
                objective
            }
            .. on StixCoreRelationship {
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
                description
                start_time
                stop_time
            }
            .. on StixSightingRelationship {
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
                description
                attribute_count
                x_opencti_negative
                first_seen
                last_seen
            }
        """

    """
        Read a StixObjectOrStixRelationship object

        :param id: the id of the StixObjectOrStixRelationship
        :return StixObjectOrStixRelationship object
    """

    def read(self, **kwargs):
        id = kwargs.get("id", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self.opencti.log(
                "info", "Reading StixObjectOrStixRelationship {" + id + "}."
            )
            query = (
                """
                query StixObjectOrStixRelationship($id: ID!) {
                    stixObjectOrStixRelationship(id: $id) {
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
                result["data"]["stixObjectOrStixRelationship"]
            )
        else:
            self.opencti.log("error", "Missing parameters: id")
            return None

    """
        Update the Identity author of a StixObjectOrStixRelationship object (created_by)

        :param id: the id of the StixObjectOrStixRelationship
        :param identity_id: the id of the Identity
        :return Boolean
    """

    def update_created_by(self, **kwargs):
        id = kwargs.get("id", None)
        identity_id = kwargs.get("identity_id", None)
        if id is not None and identity_id is not None:
            custom_attributes = """
                ... on BasicObject {
                    id
                }
                ... on BasicRelationship {
                    id
                }
                ... on StixDomainObject {
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
                }
                ... on StixCoreRelationship {
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
                }
                ... on StixSightingRelationship {
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
            # Current identity is the same
            if current_identity_id == identity_id:
                return True
            else:
                self.opencti.log(
                    "info",
                    "Updating author of StixObjectOrStixRelationship {"
                    + id
                    + "} with Identity {"
                    + identity_id
                    + "}",
                )
                # Current identity is different, delete the old relation
                if current_relation_id is not None:
                    query = """
                        mutation StixObjectOrStixRelationshipEdit($id: ID!, $relationId: ID!) {
                            stixObjectOrStixRelationshipEdit(id: $id) {
                                relationDelete(relationId: $relationId) {
                                    ... on BasicObject {
                                        id
                                    }
                                    ... on BasicRelationship {
                                        id
                                    }
                                }
                            }
                        }
                    """
                    self.opencti.query(
                        query,
                        {
                            "id": id,
                            "toId": current_identity_id,
                            "relationship_type": "created-by",
                        },
                    )
                # Add the new relation
                query = """
                   mutation StixObjectOrStixRelationshipEdit($id: ID!, $input: RelationAddInput) {
                       stixObjectOrStixRelationshipEdit(id: $id) {
                            relationAdd(input: $input) {
                                    ... on BasicObject {
                                        id
                                    }
                                    ... on BasicRelationship {
                                        id
                                    }
                            }
                       }
                   }
                """
                variables = {
                    "id": id,
                    "input": {"toId": identity_id, "relationship_type": "created-by",},
                }
                self.opencti.query(query, variables)

        else:
            self.opencti.log("error", "Missing parameters: id and identity_id")
            return False

    """
        Add a Marking-Definition object to StixObjectOrStixRelationship object (object_marking_refs)

        :param id: the id of the StixObjectOrStixRelationship
        :param marking_definition_id: the id of the Marking-Definition
        :return Boolean
    """

    def add_marking_definition(self, **kwargs):
        id = kwargs.get("id", None)
        marking_definition_id = kwargs.get("marking_definition_id", None)
        if id is not None and marking_definition_id is not None:
            custom_attributes = """
                ... on BasicObject {
                    id
                }
                ... on BasicRelationship {
                    id
                }
                ... on StixDomainObject {
                    objectMarking {
                        edges {
                            node {
                                id
                                standard_id
                                entity_type
                                definition_type
                                definition
                                x_opencti_order
                                x_opencti_color
                                created
                                modified
                            }
                        }
                    }
                }
                ... on StixCoreRelationship {
                    objectMarking {
                        edges {
                            node {
                                id
                                standard_id
                                entity_type
                                definition_type
                                definition
                                x_opencti_order
                                x_opencti_color
                                created
                                modified
                            }
                        }
                    }
                }
            """
            opencti_stix_object_or_stix_relationship = self.read(
                id=id, customAttributes=custom_attributes
            )
            if opencti_stix_object_or_stix_relationship is None:
                self.opencti.log(
                    "error", "Cannot add Marking-Definition, entity not found"
                )
                return False
            if (
                marking_definition_id
                in opencti_stix_object_or_stix_relationship["markingDefinitionsIds"]
            ):
                return True
            else:
                self.opencti.log(
                    "info",
                    "Adding Marking-Definition {"
                    + marking_definition_id
                    + "} to StixObjectOrStixRelationship {"
                    + id
                    + "}",
                )
                query = """
                   mutation StixObjectOrStixRelationshipAddRelation($id: ID!, $input: RelationAddInput) {
                       stixObjectOrStixRelationshipEdit(id: $id) {
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
                            "fromRole": "so",
                            "toId": marking_definition_id,
                            "toRole": "marking",
                            "through": "object_marking_refs",
                        },
                    },
                )
                return True
        else:
            self.opencti.log(
                "error", "Missing parameters: id and marking_definition_id"
            )
            return False

    """
        Add a Tag object to StixObjectOrStixRelationship object (tagging)

        :param id: the id of the StixObjectOrStixRelationship
        :param tag_id: the id of the Tag
        :return Boolean
    """

    def add_tag(self, **kwargs):
        id = kwargs.get("id", None)
        tag_id = kwargs.get("tag_id", None)
        if id is not None and tag_id is not None:
            custom_attributes = """
                id
                tags {
                    edges {
                        node {
                            id
                            tag_type
                            value
                            color
                        }
                    }
                }
            """
            opencti_stix_object_or_stix_relationship = self.read(
                id=id, customAttributes=custom_attributes
            )
            if opencti_stix_object_or_stix_relationship is None:
                self.opencti.log("error", "Cannot add Tag, entity not found")
                return False
            if tag_id in opencti_stix_object_or_stix_relationship["tagsIds"]:
                return True
            else:
                self.opencti.log(
                    "info",
                    "Adding Tag {"
                    + tag_id
                    + "} to StixObjectOrStixRelationship {"
                    + id
                    + "}",
                )
                query = """
                   mutation StixObjectOrStixRelationshipAddRelation($id: ID!, $input: RelationAddInput) {
                       stixObjectOrStixRelationshipEdit(id: $id) {
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
                            "fromRole": "so",
                            "toId": tag_id,
                            "toRole": "tagging",
                            "through": "tagged",
                        },
                    },
                )
                return True
        else:
            self.opencti.log("error", "Missing parameters: id and tag_id")
            return False

    """
        Add a External-Reference object to StixObjectOrStixRelationship object (object_marking_refs)

        :param id: the id of the StixObjectOrStixRelationship
        :param marking_definition_id: the id of the Marking-Definition
        :return Boolean
    """

    def add_external_reference(self, **kwargs):
        id = kwargs.get("id", None)
        external_reference_id = kwargs.get("external_reference_id", None)
        if id is not None and external_reference_id is not None:
            custom_attributes = """
                ... on BasicObject {
                    id
                }
                ... on BasicRelationship {
                    id
                }
                ... on StixDomainObject {
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
                }
                ... on StixCoreRelationship {
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
                }
                
            """
            opencti_stix_object_or_stix_relationship = self.read(
                id=id, customAttributes=custom_attributes
            )
            if opencti_stix_object_or_stix_relationship is None:
                self.opencti.log(
                    "error", "Cannot add External-Reference, entity not found"
                )
                return False
            if (
                external_reference_id
                in opencti_stix_object_or_stix_relationship["externalReferencesIds"]
            ):
                return True
            else:
                self.opencti.log(
                    "info",
                    "Adding External-Reference {"
                    + external_reference_id
                    + "} to StixObjectOrStixRelationship {"
                    + id
                    + "}",
                )
                query = """
                   mutation StixObjectOrStixRelationshipEditRelationAdd($id: ID!, $input: RelationAddInput) {
                       stixObjectOrStixRelationshipEdit(id: $id) {
                            relationAdd(input: $input) {
                                ... on BasicRelationship {
                                    id
                                }
                            }
                       }
                   }
                """
                self.opencti.query(
                    query,
                    {
                        "id": id,
                        "input": {
                            "toId": external_reference_id,
                            "relationship_type": "external-reference",
                        },
                    },
                )
                return True
        else:
            self.opencti.log(
                "error", "Missing parameters: id and external_reference_id"
            )
            return False

    """
        Add a Kill-Chain-Phase object to StixObjectOrStixRelationship object (kill_chain_phases)

        :param id: the id of the StixObjectOrStixRelationship
        :param kill_chain_phase_id: the id of the Kill-Chain-Phase
        :return Boolean
    """

    def add_kill_chain_phase(self, **kwargs):
        id = kwargs.get("id", None)
        opencti_stix_object_or_stix_relationship = kwargs.get("entity", None)
        kill_chain_phase_id = kwargs.get("kill_chain_phase_id", None)
        if id is not None and kill_chain_phase_id is not None:
            if opencti_stix_object_or_stix_relationship is None:
                opencti_stix_object_or_stix_relationship = self.read(id=id)
            if opencti_stix_object_or_stix_relationship is None:
                self.opencti.log(
                    "error", "Cannot add Kill-Chain-Phase, entity not found"
                )
                return False
            if (
                kill_chain_phase_id
                in opencti_stix_object_or_stix_relationship["killChainPhasesIds"]
            ):
                return True
            else:
                self.opencti.log(
                    "info",
                    "Adding Kill-Chain-Phase {"
                    + kill_chain_phase_id
                    + "} to StixObjectOrStixRelationship {"
                    + id
                    + "}",
                )
                query = """
                   mutation StixObjectOrStixRelationshipAddRelation($id: ID!, $input: RelationAddInput) {
                       stixObjectOrStixRelationshipEdit(id: $id) {
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
            self.opencti.log("error", "Missing parameters: id and kill_chain_phase_id")
            return False

    """
        Get the reports about a StixObjectOrStixRelationship object

        :param id: the id of the StixObjectOrStixRelationship
        :return StixObjectOrStixRelationship object
    """

    def reports(self, **kwargs):
        id = kwargs.get("id", None)
        if id is not None:
            self.opencti.log(
                "info",
                "Getting reports of the StixObjectOrStixRelationship {" + id + "}.",
            )
            query = """
                query StixObjectOrStixRelationship($id: String!) {
                    stixObjectOrStixRelationship(id: $id) {
                        reports {
                            edges {
                                node {
                                    id
                                    stix_id
                                    entity_type
                                    stix_label
                                    name
                                    alias
                                    description
                                    report_class
                                    published
                                    object_status
                                    source_confidence_level
                                    graph_data
                                    created
                                    modified
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
                                    tags {
                                        edges {
                                            node {
                                                id
                                                tag_type
                                                value
                                                color
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
                                    objectRefs {
                                        edges {
                                            node {
                                                id
                                                stix_id
                                                entity_type
                                            }
                                            relation {
                                                id
                                            }
                                        }
                                    }
                                    observableRefs {
                                        edges {
                                            node {
                                                id
                                                stix_id
                                                entity_type
                                                observable_value
                                            }
                                            relation {
                                                id
                                            }
                                        }
                                    }
                                    relationRefs {
                                        edges {
                                            node {
                                                id
                                                stix_id
                                            }
                                            relation {
                                                id
                                            }
                                        }
                                    }
                                }
                                relation {
                                    id
                                }
                            }
                        }
                    }
                }
             """
            result = self.opencti.query(query, {"id": id})
            processed_result = self.opencti.process_multiple_fields(
                result["data"]["stixObjectOrStixRelationship"]
            )
            if processed_result:
                return processed_result["reports"]
            else:
                return []
        else:
            self.opencti.log("error", "Missing parameters: id")
            return None

    """
        Get the notes about a StixObjectOrStixRelationship object

        :param id: the id of the StixObjectOrStixRelationship
        :return StixObjectOrStixRelationship object
    """

    def notes(self, **kwargs):
        id = kwargs.get("id", None)
        if id is not None:
            self.opencti.log(
                "info",
                "Getting notes of the StixObjectOrStixRelationship {" + id + "}.",
            )
            query = """
                query StixObjectOrStixRelationship($id: String!) {
                    stixObjectOrStixRelationship(id: $id) {
                        notes {
                            edges {
                                node {
                                    id
                                    stix_id
                                    entity_type
                                    stix_label
                                    name
                                    alias
                                    description
                                    content
                                    graph_data
                                    created
                                    modified
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
                                    tags {
                                        edges {
                                            node {
                                                id
                                                tag_type
                                                value
                                                color
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
                                    objectRefs {
                                        edges {
                                            node {
                                                id
                                                stix_id
                                                entity_type
                                            }
                                            relation {
                                                id
                                            }
                                        }
                                    }
                                    observableRefs {
                                        edges {
                                            node {
                                                id
                                                stix_id
                                                entity_type
                                                observable_value
                                            }
                                            relation {
                                                id
                                            }
                                        }
                                    }
                                    relationRefs {
                                        edges {
                                            node {
                                                id
                                                stix_id
                                            }
                                            relation {
                                                id
                                            }
                                        }
                                    }
                                }
                                relation {
                                    id
                                }
                            }
                        }
                    }
                }
             """
            result = self.opencti.query(query, {"id": id})
            processed_result = self.opencti.process_multiple_fields(
                result["data"]["stixObjectOrStixRelationship"]
            )
            if processed_result:
                return processed_result["notes"]
            else:
                return []
        else:
            self.opencti.log("error", "Missing parameters: id")
            return None
