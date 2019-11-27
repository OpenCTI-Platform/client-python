# coding: utf-8

import json
from pycti.utils.constants import CustomProperties


class AttackPattern:
    def __init__(self, opencti):
        self.opencti = opencti
        self.properties = """
            id
            stix_id_key
            stix_label
            entity_type
            parent_types
            name
            alias
            description
            graph_data
            platform
            required_permission
            created
            modified
            created_at
            updated_at
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
        filters = kwargs.get('filters', None)
        search = kwargs.get('search', None)
        first = kwargs.get('first', 500)
        after = kwargs.get('after', None)
        order_by = kwargs.get('orderBy', None)
        order_mode = kwargs.get('orderMode', None)
        self.opencti.log('info', 'Listing Attack-Patterns with filters ' + json.dumps(filters) + '.')
        query = """
            query AttackPatterns($filters: [AttackPatternsFiltering], $search: String, $first: Int, $after: ID, $orderBy: AttackPatternsOrdering, $orderMode: OrderingMode) {
                attackPatterns(filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
        result = self.opencti.query(query, {'filters': filters, 'search': search, 'first': first, 'after': after, 'orderBy': order_by, 'orderMode': order_mode})
        return self.opencti.process_multiple(result['data']['attackPatterns'])

    """
        Read a Attack-Pattern object
        
        :param id: the id of the Attack-Pattern
        :param filters: the filters to apply if no id provided
        :return Attack-Pattern object
    """

    def read(self, **kwargs):
        id = kwargs.get('id', None)
        filters = kwargs.get('filters', None)
        if id is not None:
            self.opencti.log('info', 'Reading Attack-Pattern {' + id + '}.')
            query = """
                query AttackPattern($id: String!) {
                    attackPattern(id: $id) {
                        """ + self.properties + """
                    }
                }
             """
            result = self.opencti.query(query, {'id': id})
            return self.opencti.process_multiple_fields(result['data']['attackPattern'])
        elif filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self.opencti.log('error', 'Missing parameters: id or filters')
            return None

    """
        Export an Attack-Pattern object in STIX2
    
        :param id: the id of the Attack-Pattern
        :return Attack-Pattern object
    """

    def to_stix2(self, **kwargs):
        id = kwargs.get('id', None)
        mode = kwargs.get('mode', 'simple')
        max_marking_definition_entity = kwargs.get('max_marking_definition_entity', None)
        entity = kwargs.get('entity', None)
        if id is not None and entity is None:
            entity = self.read(id=id)
        if entity is not None:
            attack_pattern = dict()
            attack_pattern['id'] = entity['stix_id_key']
            attack_pattern['type'] = 'attack-pattern'
            attack_pattern['name'] = entity['name']
            if self.opencti.not_empty(entity['stix_label']):
                attack_pattern['labels'] = entity['stix_label']
            else:
                attack_pattern['labels'] = ['attack-pattern']
            if self.opencti.not_empty(entity['description']): attack_pattern['description'] = entity['description']
            attack_pattern['created'] = self.opencti.stix2.format_date(entity['created'])
            attack_pattern['modified'] = self.opencti.stix2.format_date(entity['modified'])
            if self.opencti.not_empty(entity['platform']): attack_pattern['x_mitre_platforms'] = entity['platform']
            if self.opencti.not_empty(entity['required_permission']): attack_pattern['x_mitre_permissions_required'] = entity[
                'required_permission']
            if self.opencti.not_empty(entity['alias']): attack_pattern[CustomProperties.ALIASES] = entity['alias']
            attack_pattern[CustomProperties.ID] = entity['id']
            return self.opencti.stix2.prepare_export(entity, attack_pattern, mode, max_marking_definition_entity)
        else:
            self.opencti.log('error', 'Missing parameters: id or entity')
