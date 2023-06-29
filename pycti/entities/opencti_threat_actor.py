# coding: utf-8

import uuid
from typing import Union

from stix2.canonicalization.Canonicalize import canonicalize

from pycti.entities.opencti_threat_actor_group import ThreatActorGroup


class ThreatActor:
    """Main ThreatActor class for OpenCTI

    :param opencti: instance of :py:class:`~pycti.api.opencti_api_client.OpenCTIApiClient`
    """

    def __init__(self, opencti):
        """Create an instance of ThreatActor"""

        self.opencti = opencti
        self.threat_actor_group = ThreatActorGroup(opencti)

    @staticmethod
    def generate_id(name):
        name = name.lower().strip()
        data = {"name": name}
        data = canonicalize(data, utf8=False)
        id = str(uuid.uuid5(uuid.UUID("00abedb4-aa42-466c-9c01-fed23315a9b7"), data))
        return "threat-actor--" + id

    def list(self, **kwargs) -> dict:
        """List Threat-Actor objects

        The list method accepts the following kwargs:

        :param list filters: (optional) the filters to apply
        :param str search: (optional) a search keyword to apply for the listing
        :param int first: (optional) return the first n rows from the `after` ID
                            or the beginning if not set
        :param str after: (optional) OpenCTI object ID of the first row for pagination
        :param str orderBy: (optional) the field to order the response on
        :param bool orderMode: (optional) either "`asc`" or "`desc`"
        :param bool getAll: (optional) switch to return all entries (be careful to use this without any other filters)
        :param bool withPagination: (optional) switch to use pagination
        """
        return self.threat_actor_group.list(**kwargs)

    def read(self, **kwargs) -> Union[dict, None]:
        """Read a Threat-Actor object

        read can be either used with a known OpenCTI entity `id` or by using a
        valid filter to search and return a single Threat-Actor entity or None.

        The list method accepts the following kwargs.

        Note: either `id` or `filters` is required.

        :param str id: the id of the Threat-Actor
        :param list filters: the filters to apply if no id provided
        """
        return self.threat_actor_group.read(**kwargs)

    def create(self, **kwargs):
        """Create a Threat-Actor object

        The Threat-Actor entity will only be created if it doesn't exists
        By setting `update` to `True` it acts like an upsert and updates
        fields of an existing Threat-Actor entity.

        The create method accepts the following kwargs.

        Note: `name` and `description` or `stix_id` is required.

        :param str stix_id: stix2 id reference for the Threat-Actor entity
        :param str createdBy: (optional) id of the organization that created the knowledge
        :param list objectMarking: (optional) list of OpenCTI markin definition ids
        :param list objectLabel: (optional) list of OpenCTI label ids
        :param list externalReferences: (optional) list of OpenCTI external references ids
        :param bool revoked: is this entity revoked
        :param int confidence: confidence level
        :param str lang: language
        :param str created: (optional) date in OpenCTI date format
        :param str modified: (optional) date in OpenCTI date format
        :param str name: name of the threat actor
        :param str description: description of the threat actor
        :param list aliases: (optional) list of alias names for the Threat-Actor
        :param list threat_actor_types: (optional) list of threat actor types
        :param str first_seen: (optional) date in OpenCTI date format
        :param str last_seen: (optional) date in OpenCTI date format
        :param list roles: (optional) list of roles
        :param list goals: (optional) list of goals
        :param str sophistication: (optional) describe the actors sophistication in text
        :param str resource_level: (optional) describe the actors resource_level in text
        :param str primary_motivation: (optional) describe the actors primary_motivation in text
        :param list secondary_motivations: (optional) describe the actors secondary_motivations in list of string
        :param list personal_motivations: (optional) describe the actors personal_motivations in list of strings
        :param bool update: (optional) choose to updated an existing Threat-Actor entity, default `False`
        """
        return self.threat_actor_group.create(**kwargs)

    """
        Import an Threat-Actor object from a STIX2 object

        :param stixObject: the Stix-Object Intrusion-Set
        :return Intrusion-Set object
    """

    def import_from_stix2(self, **kwargs):
        return self.threat_actor_group.import_from_stix2(**kwargs)
