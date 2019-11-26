# coding: utf-8

class StixRelation:
    def __init__(self, opencti):
        self.opencti = opencti
        self.properties = """
            id
            stix_id_key
            entity_type
            relationship_type
            description
            weight
            role_played
            score
            expiration
            first_seen
            last_seen
            created
            modified
            created_at
            updated_at
            from {
                id
                stix_id_key
            }
            to {
                id
                stix_id_key
            }
            createdByRef {
                node {
                    id
                    entity_type
                    stix_id_key
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
                        stix_id_key
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
                        stix_id_key
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
        """

    """
        List Stix-Relation objects

        :param fromId: the id of the source entity of the relation
        :param toId: the id of the target entity of the relation
        :param relationType: the relation type
        :param firstSeenStart: the first_seen date start filter
        :param firstSeenStop: the first_seen date stop filter
        :param lastSeenStart: the last_seen date start filter
        :param lastSeenStop: the last_seen date stop filter
        :param inferred: includes inferred relations
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination        
        :return List of Stix-Relation objects
    """

    def list(self, **kwargs):
        from_id = kwargs.get('fromId', None)
        from_types = kwargs.get('fromTypes', None)
        to_id = kwargs.get('toId', None)
        to_types = kwargs.get('toTypes', None)
        relation_type = kwargs.get('relationType', None)
        first_seen_start = kwargs.get('firstSeenStart', None)
        first_seen_stop = kwargs.get('firstSeenStop', None)
        last_seen_start = kwargs.get('lastSeenStart', None)
        last_seen_stop = kwargs.get('lastSeenStop', None)
        inferred = kwargs.get('inferred', None)
        first = kwargs.get('first', 500)
        after = kwargs.get('after', None)
        self.opencti.log('info', 'Listing Stix-Relations with filters.')
        query = """
            query StixRelations($fromId: String, $fromTypes: [String], $toId: String, $toTypes: [String], $relationType: String, $firstSeenStart: DateTime, $firstSeenStop: DateTime, $lastSeenStart: DateTime, $lastSeenStop: DateTime, $inferred: Boolean, $first: Int, $after: ID) {
                stixRelations(fromId: $fromId, fromTypes: $fromTypes, toId: $toId, toTypes: $toTypes, relationType: $relationType, firstSeenStart: $firstSeenStart, firstSeenStop: $firstSeenStop, lastSeenStart: $lastSeenStart, lastSeenStop: $lastSeenStop, inferred: $inferred, first: $first, after: $after) {
                    edges {
                        node {
                            """ + self.properties + """
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
        result = self.opencti.query(query, {
            'fromId': from_id,
            'fromTypes': from_types,
            'toId': to_id,
            'toTypes': to_types,
            'relationType': relation_type,
            'firstSeenStart': first_seen_start,
            'firstSeenStop': first_seen_stop,
            'lastSeenStart': last_seen_start,
            'lastSeenStop': last_seen_stop,
            'inferred': inferred,
            'first': first,
            'after': after
        })
        return self.opencti.process_multiple(result['data']['stixRelations'])

    """
        Read a Stix-Relation object
        
        :param id: the id of the Stix-Relation
        :param stix_id_key: the STIX id of the Stix-Relation
        :param fromId: the id of the source entity of the relation
        :param toId: the id of the target entity of the relation
        :param relationType: the relation type
        :param firstSeenStart: the first_seen date start filter
        :param firstSeenStop: the first_seen date stop filter
        :param lastSeenStart: the last_seen date start filter
        :param lastSeenStop: the last_seen date stop filter
        :param inferred: includes inferred relations
        :return Stix-Relation object
    """

    def read(self, **kwargs):
        id = kwargs.get('id', None)
        stix_id_key = kwargs.get('stix_id_key', None)
        from_id = kwargs.get('fromId', None)
        to_id = kwargs.get('toId', None)
        relation_type = kwargs.get('relationType', None)
        first_seen_start = kwargs.get('firstSeenStart', None)
        first_seen_stop = kwargs.get('firstSeenStop', None)
        last_seen_start = kwargs.get('lastSeenStart', None)
        last_seen_stop = kwargs.get('lastSeenStop', None)
        inferred = kwargs.get('inferred', None)
        if id is not None:
            self.opencti.log('info', 'Reading Stix-Relation {' + id + '}.')
            query = """
                query StixRelation($id: String!) {
                    stixRelation(id: $id) {
                        """ + self.properties + """
                    }
                }
             """
            result = self.opencti.query(query, {'id': id})
            return self.opencti.process_multiple_fields(result['data']['stixRelation'])
        elif stix_id_key is not None:
            self.opencti.log('info', 'Reading Stix-Relation with stix_id_key {' + stix_id_key + '}.')
            query = """
                query StixRelation($stix_id_key: String!) {
                    stixRelation(stix_id_key: $stix_id_key) {
                        """ + self.properties + """
                    }
                }
             """
            result = self.opencti.query(query, {'stix_id_key': stix_id_key})
            return self.opencti.process_multiple_fields(result['data']['stixRelation'])
        else:
            result = self.list(
                fromId=from_id,
                toId=to_id,
                relationType=relation_type,
                firstSeenStart=first_seen_start,
                firstSeenStop=first_seen_stop,
                lastSeenStart=last_seen_start,
                lastSeenStop=last_seen_stop,
                inferred=inferred
            )
            if len(result) > 0:
                return result[0]
            else:
                return None

    """
        Update a Stix-Relation object field

        :param id: the Stix-Relation id
        :param key: the key of the field
        :param value: the value of the field
        :return The updated Stix-Relation object
    """

    def update_field(self, **kwargs):
        id = kwargs.get('id', None)
        key = kwargs.get('key', None)
        value = kwargs.get('key', None)
        if id is not None and key is not None and value is not None:
            self.opencti.log('info', 'Updatating Stix-Relation {' + id + '} field {' + key + '}.')
            query = """
                mutation StixRelationEdit($id: ID!, $input: EditInput!) {
                    stixRelationEdit(id: $id) {
                        fieldPatch(input: $input) {
                            """ + self.properties + """
                        }
                    }
                }
            """
            result = self.opencti.query(query, {
                'id': id,
                'input': {
                    'key': key,
                    'value': value
                }
            })
            return self.opencti.process_multiple_fields(result['data']['stixRelationEdit']['fieldPatch'])
        else:
            self.opencti.log('error', 'Missing parameters: id and key and value')
            return None

    """
        Add a Kill-Chain-Phase object to Stix-Relation object (kill_chain_phases)

        :param id: the id of the Stix-Relation
        :param kill_chain_phase_id: the id of the Kill-Chain-Phase
        :return Boolean
    """

    def add_kill_chain_phase(self, **kwargs):
        id = kwargs.get('id', None)
        kill_chain_phase_id = kwargs.get('kill_chain_phase_id', None)
        if id is not None and kill_chain_phase_id is not None:
            self.opencti.log('info',
                             'Adding Kill-Chain-Phase {' + kill_chain_phase_id + '} to Stix-Entity {' + id + '}')
            stix_entity = self.read(id=id)
            kill_chain_phases_ids = []
            for marking in stix_entity['killChainPhases']:
                kill_chain_phases_ids.append(marking['id'])
            if kill_chain_phase_id in kill_chain_phases_ids:
                return True
            else:
                query = """
                   mutation StixRelationAddRelation($id: ID!, $input: RelationAddInput) {
                       stixRelationEdit(id: $id) {
                            relationAdd(input: $input) {
                                node {
                                    id
                                }
                            }
                       }
                   }
                """
                self.opencti.query(query, {
                    'id': id,
                    'input': {
                        'fromRole': 'phase_belonging',
                        'toId': kill_chain_phase_id,
                        'toRole': 'kill_chain_phase',
                        'through': 'kill_chain_phases'
                    }
                })
                return True
        else:
            self.opencti.log('error', 'Missing parameters: id and kill_chain_phase_id')
            return False
