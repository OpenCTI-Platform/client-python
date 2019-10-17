import logging


class OpenCTIApiCity:

    def __init__(self, api):
        self.api = api

    def create_city(self, city_name, id=None, stix_id_key=None, created=None, modified=None):
        logging.info('Creating city ' + city_name + '...')
        query = """
               mutation CityAdd($input: CityAddInput) {
                   cityAdd(input: $input) {
                       id
                   }
               }
           """
        result = self.api.query(query, {
            'input': {
                'name': city_name,
                'internal_id_key': id,
                'stix_id_key': stix_id_key,
                'created': created,
                'modified': modified
            }
        })
        return result['data']['cityAdd']
