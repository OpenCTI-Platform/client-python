# coding: utf-8

class KillChainPhase:
    def __init__(self, opencti):
        self.opencti = opencti
        self.properties = """
            id
            entity_type
            stix_id_key
            kill_chain_name
            phase_name
            phase_order
            created
            modified
            created_at
            updated_at
        """

    """
        List Kill-Chain-Phase objects

        :param filters: the filters to apply
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of Kill-Chain-Phase objects
    """

    def list(self, **kwargs):
        filters = kwargs.get('filters', None)
        first = kwargs.get('first', 500)
        after = kwargs.get('after', None)
        self.opencti.log('info', 'Listing Kill-Chain-Phase with filters.')
        query = """
            query KillChainPhases($filters: [KillChainPhasesFiltering], $first: Int, $after: ID) {
                killChainPhases(filters: $filters, first: $first, after: $after) {
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
        result = self.opencti.query(query, {'filters': filters, 'first': first, 'after': after})
        return self.opencti.process_multiple(result['data']['killChainPhases'])

    """
        Read a Kill-Chain-Phase object

        :param id: the id of the Kill-Chain-Phase
        :param filters: the filters to apply if no id provided
        :return Kill-Chain-Phase object
    """

    def read(self, **kwargs):
        id = kwargs.get('id', None)
        filters = kwargs.get('filters', None)
        if id is not None:
            self.opencti.log('info', 'Reading Kill-Chain-Phase {' + id + '}.')
            query = """
                query KillChainPhase($id: String!) {
                    killChainPhase(id: $id) {
                        """ + self.properties + """
                    }
                }
            """
            result = self.opencti.query(query, {'id': id})
            return self.opencti.process_multiple_fields(result['data']['killChainPhase'])
        elif filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self.opencti.log('error', 'Missing parameters: id or filters')
            return None