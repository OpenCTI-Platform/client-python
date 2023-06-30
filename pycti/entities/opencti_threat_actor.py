
from pycti.entities.opencti_threat_actor_group import ThreatActorGroup
from pycti.entities.opencti_threat_actor_individual import ThreatActorIndividual
class ThreatActor:
    """Main ThreatActor class for OpenCTI

    :param opencti: instance of :py:class:`~pycti.api.opencti_api_client.OpenCTIApiClient`
    """
    def __init__(self, opencti):
        """Create an instance of ThreatActor"""

        self.opencti = opencti

    def import_from_stix2(self, **kwargs):
        stix_object = kwargs.get("stixObject", None)
        if "x_opencti_category" in stix_object:
            type = stix_object["x_opencti_category"]
        elif self.opencti.get_attribute_in_extension("type", stix_object) is not None:
            type = self.opencti.get_attribute_in_extension("type", stix_object)
        elif "individual" in stix_object["resource_level"]:
            type = "Threat-Actor-Individual"
        else:
            type = "Threat-Actor-Group"
        if "threat-actor-group" in type:
            return ThreatActorGroup.import_from_stix2(self, kwargs)
        if "threat-actor-individual" in type:
            return ThreatActorIndividual.import_from_stix2(self, kwargs)
