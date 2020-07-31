"""These are the custom STIX properties and observation types used internally by OpenCTI.

"""
from enum import Enum


class StixCyberObservableTypes(Enum):
    AUTONOMOUS_SYSTEM = "Autonomous-System"
    DIRECTORY = "Directory"
    DOMAIN_NAME = "Domain-Name"
    EMAIL_ADDR = "Email-Addr"
    EMAIL_MESSAGE = "Email-Message"
    EMAIL_MIME_PART_TYPE = "Email-Mime-Part-Type"
    ARTIFACT = "Artifact"
    FILE = "File"
    X509_CERTIFICATE = "X509-Certificate"
    IPV4_ADDR = "IPv4-Addr"
    IPV6_ADDR = "IPv6-Addr"
    MAC_ADDR = "Mac-Addr"
    MUTEX = "Mutex"
    NETWORK_TRAFFIC = "Network-Traffic"
    PROCESS = "Process"
    SOFTWARE = "Software"
    URL = "Url"
    USER_ACCOUNT = "User-Account"
    WINDOWS_REGISTRY_KEY = "Windows-Registry-Key"
    WINDOWS_REGISTRY_VALUE_TYPE = "Windows-Registry-Value-Type"
    X509_V3_EXTENSIONS_TYPE_ = "X509-V3-Extensions-Type"
    X_OPENCTI_CRYPTOGRAPHIC_KEY = "X-Opencti-Cryptographic-Key"
    X_OPENCTI_CRYPTOCURRENCY_WALLET = "X-Opencti-Cryptocurrency-Wallet"
    X_OPENCTI_TEXT = "X-Opencti-Text"
    X_OPENCTI_USER_AGENT = "X-Opencti-User-Agent"

    @classmethod
    def has_value(cls, value):
        lower_attr = list(map(lambda x: x.lower(), cls._value2member_map_))
        return value in lower_attr


class IdentityTypes(Enum):
    SECTOR = "Sector"
    ORGANIZATION = "Organization"
    INDIVIDUAL = "Individual"

    @classmethod
    def has_value(cls, value):
        lower_attr = list(map(lambda x: x.lower(), cls._value2member_map_))
        return value in lower_attr


class LocationTypes(Enum):
    CITY = "City"
    COUNTRY = "Country"
    REGION = "Region"
    POSITION = "Position"

    @classmethod
    def has_value(cls, value):
        lower_attr = list(map(lambda x: x.lower(), cls._value2member_map_))
        return value in lower_attr


class CustomProperties:
    """These are the custom properties used by OpenCTI.
    """

    # internal id used by OpenCTI - this will be auto generated
    ID = "x_opencti_id"

    # List of files
    FILES = "x_opencti_files"

    # This should be set on all reports to one of the following values:
    #  "external"
    #  "internal"
    REPORT_CLASS = "x_opencti_report_class"

    # use with observed_data and indicators
    INDICATOR_PATTERN = "x_opencti_indicator_pattern"
    PATTERN_TYPE = "x_opencti_pattern_type"
    OBSERVABLE_TYPE = "x_opencti_observable_type"
    OBSERVABLE_VALUE = "x_opencti_observable_value"
    DETECTION = "x_opencti_detection"
    CREATE_OBSERVABLES = "x_opencti_observables_create"
    CREATE_INDICATOR = "x_opencti_indicator_create"

    # custom created and modified dates
    # use with STIX "kill chain" and "external reference" objects
    CREATED = "x_opencti_created"
    MODIFIED = "x_opencti_modified"

    # use with attack pattern
    EXTERNAL_ID = "x_opencti_external_id"

    # use with vulnerability
    BASE_SCORE = "x_opencti_base_score"
    BASE_SEVERITY = "x_opencti_base_severity"
    ATTACK_VECTOR = "x_opencti_attack_vector"
    INTEGRITY_IMPACT = "x_opencti_integrity_impact"
    AVAILABILITY_IMPACT = "x_opencti_availability_impact"

    # use with intrusion-set, campaign, relation
    FIRST_SEEN = "x_opencti_first_seen"
    LAST_SEEN = "x_opencti_last_seen"

    # use with marking definitions
    COLOR = "x_opencti_color"
    LEVEL = "x_opencti_level"  # should be an integer

    # use with kill chain
    PHASE_ORDER = "x_opencti_phase_order"

    # use with relation
    WEIGHT = "x_opencti_weight"
    SCORE = "x_opencti_score"
    ROLE_PLAYED = "x_opencti_role_played"
    EXPIRATION = "x_opencti_expiration"
    SOURCE_REF = "x_opencti_source_ref"
    TARGET_REF = "x_opencti_target_ref"
    IGNORE_DATES = "x_opencti_ignore_dates"
    NEGATIVE = "x_opencti_false_positive"

    # generic property - applies to most SDOs
    ALIASES = "x_opencti_aliases"

    # applies to STIX Identity
    ORG_CLASS = "x_opencti_x_opencti_organization_type"
    x_opencti_reliability = "x_opencti_x_opencti_reliability"
    IDENTITY_TYPE = (
        "x_opencti_identity_type"  # this overrides the stix 'identity_class' property!
    )
    TAG_TYPE = "x_opencti_tags"

    # applies to STIX report
    OBJECT_STATUS = "x_opencti_object_status"
    SRC_CONF_LEVEL = "x_opencti_source_confidence_level"
    GRAPH_DATA = "x_opencti_graph_data"

    # applies to STIX note
    NAME = "x_opencti_name"
