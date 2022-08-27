"""OpenCTI SCO operations"""

import json
import os
from typing import TYPE_CHECKING, Type

import magic

if TYPE_CHECKING:
    from ..api.opencti_api_client import OpenCTIApiClient


__all__ = [
    "StixCyberObservable",
]


class StixCyberObservable:
    """SCO objects"""

    def __init__(self, api: "OpenCTIApiClient", file_type: Type):
        """
        Constructor.

        :param api: OpenCTI API client
        :param file_type: File upload class type
        """

        self.opencti = api
        self._file_type = file_type
        self.properties = """
            id
            standard_id
            entity_type
            parent_types
            spec_version
            created_at
            updated_at
            createdBy {
                ... on Identity {
                    id
                    standard_id
                    entity_type
                    parent_types
                    spec_version
                    identity_class
                    name
                    description
                    roles
                    contact_information
                    x_opencti_aliases
                    created
                    modified
                    objectLabel {
                        edges {
                            node {
                                id
                                value
                                color
                            }
                        }
                    }
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
                        importFiles {
                            edges {
                                node {
                                    id
                                    name
                                    size
                                    metaData {
                                        mimetype
                                        version
                                    }
                                }
                            }
                        }
                    }
                }
            }
            observable_value
            x_opencti_description
            x_opencti_score
            indicators {
                edges {
                    node {
                        id
                        pattern
                        pattern_type
                    }
                }
            }
            ... on AutonomousSystem {
                number
                name
                rir
            }
            ... on Directory {
                path
                path_enc
                ctime
                mtime
                atime
            }
            ... on DomainName {
                value
            }
            ... on EmailAddr {
                value
                display_name
            }
            ... on EmailMessage {
                is_multipart
                attribute_date
                content_type
                message_id
                subject
                received_lines
                body
            }
            ... on Artifact {
                mime_type
                payload_bin
                url
                encryption_algorithm
                decryption_key
                hashes {
                    algorithm
                    hash
                }
                importFiles {
                    edges {
                        node {
                            id
                            name
                            size
                        }
                    }
                }
            }
            ... on StixFile {
                extensions
                size
                name
                name_enc
                magic_number_hex
                mime_type
                ctime
                mtime
                atime
                x_opencti_additional_names
                hashes {
                  algorithm
                  hash
                }
            }
            ... on X509Certificate {
                is_self_signed
                version
                serial_number
                signature_algorithm
                issuer
                subject
                subject_public_key_algorithm
                subject_public_key_modulus
                subject_public_key_exponent
                validity_not_before
                validity_not_after
                hashes {
                  algorithm
                  hash
                }
            }
            ... on IPv4Addr {
                value
            }
            ... on IPv6Addr {
                value
            }
            ... on MacAddr {
                value
            }
            ... on Mutex {
                name
            }
            ... on NetworkTraffic {
                extensions
                start
                end
                is_active
                src_port
                dst_port
                protocols
                src_byte_count
                dst_byte_count
                src_packets
                dst_packets
            }
            ... on Process {
                extensions
                is_hidden
                pid
                created_time
                cwd
                command_line
                environment_variables
            }
            ... on Software {
                name
                cpe
                swid
                languages
                vendor
                version
            }
            ... on Url {
                value
            }
            ... on UserAccount {
                extensions
                user_id
                credential
                account_login
                account_type
                display_name
                is_service_account
                is_privileged
                can_escalate_privs
                is_disabled
                account_created
                account_expires
                credential_last_changed
                account_first_login
                account_last_login
            }
            ... on WindowsRegistryKey {
                attribute_key
                modified_time
                number_of_subkeys
            }
            ... on WindowsRegistryValueType {
                name
                data
                data_type
            }
            ... on CryptographicKey {
                value
            }
            ... on CryptocurrencyWallet {
                value
            }
            ... on Hostname {
                value
            }
            ... on Text {
                value
            }
            ... on UserAgent {
                value
            }
            importFiles {
                edges {
                    node {
                        id
                        name
                        size
                        metaData {
                            mimetype
                            version
                        }
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
        first = kwargs.get("first", 100)
        after = kwargs.get("after", None)
        order_by = kwargs.get("orderBy", None)
        order_mode = kwargs.get("orderMode", None)
        custom_attributes = kwargs.get("customAttributes", None)
        get_all = kwargs.get("getAll", False)
        with_pagination = kwargs.get("withPagination", False)

        if get_all:
            first = 100

        self.opencti.log(
            "info",
            "Listing StixCyberObservables with filters " + json.dumps(filters) + ".",
        )
        query = (
            """
                    query StixCyberObservables($types: [String], $filters: [StixCyberObservablesFiltering], $search: String, $first: Int, $after: ID, $orderBy: StixCyberObservablesOrdering, $orderMode: OrderingMode) {
                        stixCyberObservables(types: $types, filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
            data = self.opencti.process_multiple(result["data"]["stixCyberObservables"])
            final_data = final_data + data
            while result["data"]["stixCyberObservables"]["pageInfo"]["hasNextPage"]:
                after = result["data"]["stixCyberObservables"]["pageInfo"]["endCursor"]
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
                    result["data"]["stixCyberObservables"]
                )
                final_data = final_data + data
            return final_data
        else:
            return self.opencti.process_multiple(
                result["data"]["stixCyberObservables"], with_pagination
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
                            stixCyberObservable(id: $id) {
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
                result["data"]["stixCyberObservable"]
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
        Upload a file in this Observable

        :param id: the Stix-Cyber-Observable id
        :param file_name
        :param data
        :return void
    """

    def add_file(self, **kwargs):
        id = kwargs.get("id", None)
        file_name = kwargs.get("file_name", None)
        data = kwargs.get("data", None)
        mime_type = kwargs.get("mime_type", "text/plain")
        if id is not None and file_name is not None:
            final_file_name = os.path.basename(file_name)
            query = """
                    mutation StixCyberObservableEdit($id: ID!, $file: Upload!) {
                        stixCyberObservableEdit(id: $id) {
                            importPush(file: $file) {
                                id
                                name
                            }
                        }
                    }
                 """
            if data is None:
                data = open(file_name, "rb")
                if file_name.endswith(".json"):
                    mime_type = "application/json"
                else:
                    mime_type = magic.from_file(file_name, mime=True)
            self.opencti.log(
                "info",
                "Uploading a file {"
                + final_file_name
                + "} in Stix-Cyber-Observable {"
                + id
                + "}.",
            )
            return self.opencti.query(
                query,
                {"id": id, "file": (self._file_type(final_file_name, data, mime_type))},
            )
        else:
            self.opencti.log(
                "error",
                "[opencti_stix_cyber_observable Missing parameters: id or file_name",
            )
            return None

    """
        Create a Stix-Observable object

        :param observableData: the data of the observable (STIX2 structure)
        :return Stix-Observable object
    """

    def create(self, **kwargs):
        observable_data = kwargs.get("observableData", {})
        simple_observable_id = kwargs.get("simple_observable_id", None)
        simple_observable_key = kwargs.get("simple_observable_key", None)
        simple_observable_value = kwargs.get("simple_observable_value", None)
        simple_observable_description = kwargs.get(
            "simple_observable_description", None
        )
        x_opencti_score = kwargs.get("x_opencti_score", None)
        created_by = kwargs.get("createdBy", None)
        object_marking = kwargs.get("objectMarking", None)
        object_label = kwargs.get("objectLabel", None)
        external_references = kwargs.get("externalReferences", None)
        update = kwargs.get("update", False)

        create_indicator = (
            observable_data["x_opencti_create_indicator"]
            if "x_opencti_create_indicator" in observable_data
            else kwargs.get("createIndicator", False)
        )
        attribute = None
        if simple_observable_key is not None:
            key_split = simple_observable_key.split(".")
            type = key_split[0].title()
            attribute = key_split[1]
            if attribute not in ["hashes", "extensions"]:
                observable_data[attribute] = simple_observable_value
        else:
            type = (
                observable_data["type"].title() if "type" in observable_data else None
            )
        if type is None:
            return
        if type.lower() == "file":
            type = "StixFile"
        elif type.lower() == "ipv4-addr":
            type = "IPv4-Addr"
        elif type.lower() == "ipv6-addr":
            type = "IPv6-Addr"
        elif type.lower() == "hostname" or type.lower() == "x-opencti-hostname":
            type = "Hostname"
        elif (
            type.lower() == "cryptocurrency-wallet"
            or type.lower() == "x-opencti-cryptocurrency-wallet"
        ):
            type = "Cryptocurrency-Wallet"
        elif type.lower() == "user-agent" or type.lower() == "x-opencti-user-agent":
            type = "User-Agent"
        elif (
            type.lower() == "cryptographic-key"
            or type.lower() == "x-opencti-cryptographic-key"
        ):
            type = "Cryptographic-Key"
        elif type.lower() == "text" or type.lower() == "x-opencti-text":
            type = "Text"

        if "x_opencti_description" in observable_data:
            x_opencti_description = observable_data["x_opencti_description"]
        else:
            x_opencti_description = self.opencti.get_attribute_in_extension(
                "description", observable_data
            )

        if simple_observable_description is not None:
            x_opencti_description = simple_observable_description

        if "x_opencti_score" in observable_data:
            x_opencti_score = observable_data["x_opencti_score"]
        elif (
            self.opencti.get_attribute_in_extension("score", observable_data)
            is not None
        ):
            x_opencti_score = self.opencti.get_attribute_in_extension(
                "score", observable_data
            )

        stix_id = observable_data["id"] if "id" in observable_data else None
        if simple_observable_id is not None:
            stix_id = simple_observable_id

        hashes = []
        if (
            simple_observable_key is not None
            and simple_observable_key.lower() == "file.hashes.md5"
        ):
            hashes.append({"algorithm": "MD5", "hash": simple_observable_value})
        if (
            simple_observable_key is not None
            and simple_observable_key.lower() == "file.hashes.sha-1"
        ):
            hashes.append({"algorithm": "SHA-1", "hash": simple_observable_value})
        if (
            simple_observable_key is not None
            and simple_observable_key.lower() == "file.hashes.sha-256"
        ):
            hashes.append({"algorithm": "SHA-256", "hash": simple_observable_value})
        if "hashes" in observable_data:
            for key, value in observable_data["hashes"].items():
                hashes.append({"algorithm": key, "hash": value})

        if type is not None:
            self.opencti.log(
                "info",
                "Creating Stix-Cyber-Observable {"
                + type
                + "} with indicator at "
                + str(create_indicator)
                + ".",
            )
            input_variables = {
                "type": type,
                "stix_id": stix_id,
                "x_opencti_score": x_opencti_score,
                "x_opencti_description": x_opencti_description,
                "createIndicator": create_indicator,
                "createdBy": created_by,
                "objectMarking": object_marking,
                "objectLabel": object_label,
                "externalReferences": external_references,
                "update": update,
            }
            query = """
                mutation StixCyberObservableAdd(
                    $type: String!,
                    $stix_id: String,
                    $x_opencti_score: Int,
                    $x_opencti_description: String,
                    $createIndicator: Boolean,
                    $createdBy: String,
                    $objectMarking: [String],
                    $objectLabel: [String],
                    $externalReferences: [String],
                    $AutonomousSystem: AutonomousSystemAddInput,
                    $Directory: DirectoryAddInput,
                    $DomainName: DomainNameAddInput,
                    $EmailAddr: EmailAddrAddInput,
                    $EmailMessage: EmailMessageAddInput,
                    $EmailMimePartType: EmailMimePartTypeAddInput,
                    $Artifact: ArtifactAddInput,
                    $StixFile: StixFileAddInput,
                    $X509Certificate: X509CertificateAddInput,
                    $IPv4Addr: IPv4AddrAddInput,
                    $IPv6Addr: IPv6AddrAddInput,
                    $MacAddr: MacAddrAddInput,
                    $Mutex: MutexAddInput,
                    $NetworkTraffic: NetworkTrafficAddInput,
                    $Process: ProcessAddInput,
                    $Software: SoftwareAddInput,
                    $Url: UrlAddInput,
                    $UserAccount: UserAccountAddInput,
                    $WindowsRegistryKey: WindowsRegistryKeyAddInput,
                    $WindowsRegistryValueType: WindowsRegistryValueTypeAddInput,
                    $CryptographicKey: CryptographicKeyAddInput,
                    $CryptocurrencyWallet: CryptocurrencyWalletAddInput,
                    $Hostname: HostnameAddInput
                    $Text: TextAddInput,
                    $UserAgent: UserAgentAddInput
                ) {
                    stixCyberObservableAdd(
                        type: $type,
                        stix_id: $stix_id,
                        x_opencti_score: $x_opencti_score,
                        x_opencti_description: $x_opencti_description,
                        createIndicator: $createIndicator,
                        createdBy: $createdBy,
                        objectMarking: $objectMarking,
                        objectLabel: $objectLabel,
                        externalReferences: $externalReferences,
                        AutonomousSystem: $AutonomousSystem,
                        Directory: $Directory,
                        DomainName: $DomainName,
                        EmailAddr: $EmailAddr,
                        EmailMessage: $EmailMessage,
                        EmailMimePartType: $EmailMimePartType,
                        Artifact: $Artifact,
                        StixFile: $StixFile,
                        X509Certificate: $X509Certificate,
                        IPv4Addr: $IPv4Addr,
                        IPv6Addr: $IPv6Addr,
                        MacAddr: $MacAddr,
                        Mutex: $Mutex,
                        NetworkTraffic: $NetworkTraffic,
                        Process: $Process,
                        Software: $Software,
                        Url: $Url,
                        UserAccount: $UserAccount,
                        WindowsRegistryKey: $WindowsRegistryKey,
                        WindowsRegistryValueType: $WindowsRegistryValueType,
                        CryptographicKey: $CryptographicKey,
                        CryptocurrencyWallet: $CryptocurrencyWallet,
                        Hostname: $Hostname,
                        Text: $Text,
                        UserAgent: $UserAgent
                    ) {
                        id
                        standard_id
                        entity_type
                        parent_types
                        indicators {
                            edges {
                                node {
                                    id
                                    pattern
                                    pattern_type
                                }
                            }
                        }
                    }
                }
            """
            if type == "Autonomous-System":
                input_variables["AutonomousSystem"] = {
                    "number": observable_data["number"],
                    "name": observable_data.get("name"),
                    "rir": observable_data.get("rir"),
                }
            elif type == "Directory":
                input_variables["Directory"] = {
                    "path": observable_data["path"],
                    "path_enc": observable_data.get("path_enc"),
                    "ctime": observable_data.get("ctime"),
                    "mtime": observable_data.get("mtime"),
                    "atime": observable_data.get("atime"),
                }
            elif type == "Domain-Name":
                input_variables["DomainName"] = {"value": observable_data["value"]}
                if attribute is not None:
                    input_variables["DomainName"][attribute] = simple_observable_value
            elif type == "Email-Addr":
                input_variables["EmailAddr"] = {
                    "value": observable_data["value"],
                    "display_name": observable_data.get("display_name"),
                }
            elif type == "Email-Message":
                input_variables["EmailMessage"] = {
                    "is_multipart": observable_data.get("is_multipart"),
                    "attribute_date": observable_data.get("date"),
                    "message_id": observable_data.get("message_id"),
                    "subject": observable_data.get("subject"),
                    "received_lines": observable_data.get("received_lines"),
                    "body": observable_data.get("body"),
                }
            elif type == "Email-Mime-Part-Type":
                input_variables["EmailMimePartType"] = {
                    "body": observable_data.get("body"),
                    "content_type": observable_data.get("content_type"),
                    "content_disposition": observable_data.get("content_disposition"),
                }
            elif type == "Artifact":
                input_variables["Artifact"] = {
                    "hashes": hashes if len(hashes) > 0 else None,
                    "mime_type": observable_data.get("mime_type"),
                    "payload_bin": observable_data.get("payload_bin"),
                    "url": observable_data.get("url"),
                    "encryption_algorithm": observable_data.get("encryption_algorithm"),
                    "decryption_key": observable_data.get("decryption_key"),
                }
            elif type == "StixFile":
                if (
                    "x_opencti_additional_names" not in observable_data
                    and self.opencti.get_attribute_in_extension(
                        "x_opencti_additional_names", observable_data
                    )
                    is not None
                ):
                    observable_data[
                        "x_opencti_additional_names"
                    ] = self.opencti.get_attribute_in_extension(
                        "x_opencti_additional_names", observable_data
                    )
                input_variables["StixFile"] = {
                    "hashes": hashes if len(hashes) > 0 else None,
                    "size": observable_data.get("size"),
                    "name": observable_data.get("name"),
                    "name_enc": observable_data.get("name_enc"),
                    "magic_number_hex": observable_data.get("magic_number_hex"),
                    "mime_type": observable_data.get("mime_type"),
                    "mtime": observable_data.get("mtime"),
                    "ctime": observable_data.get("ctime"),
                    "atime": observable_data.get("atime"),
                    "x_opencti_additional_names": observable_data[
                        "x_opencti_additional_names"
                    ]
                    if "x_opencti_additional_names" in observable_data
                    else None,
                }
            elif type == "X509-Certificate":
                input_variables["X509Certificate"] = {
                    "hashes": hashes if len(hashes) > 0 else None,
                    "is_self_signed": observable_data["is_self_signed"]
                    if "is_self_signed" in observable_data
                    else False,
                    "version": observable_data.get("version"),
                    "serial_number": observable_data.get("serial_number"),
                    "signature_algorithm": observable_data.get("signature_algorithm"),
                    "issuer": observable_data.get("issuer"),
                    "validity_not_before": observable_data.get("validity_not_before"),
                    "validity_not_after": observable_data.get("validity_not_after"),
                    "subject": observable_data.get("subject"),
                    "subject_public_key_algorithm": observable_data[
                        "subject_public_key_algorithm"
                    ]
                    if "subject_public_key_algorithm" in observable_data
                    else None,
                    "subject_public_key_modulus": observable_data[
                        "subject_public_key_modulus"
                    ]
                    if "subject_public_key_modulus" in observable_data
                    else None,
                    "subject_public_key_exponent": observable_data[
                        "subject_public_key_exponent"
                    ]
                    if "subject_public_key_exponent" in observable_data
                    else None,
                }
            elif type == "IPv4-Addr":
                input_variables["IPv4Addr"] = {
                    "value": observable_data.get("value"),
                }
            elif type == "IPv6-Addr":
                input_variables["IPv6Addr"] = {
                    "value": observable_data.get("value"),
                }
            elif type == "Mac-Addr":
                input_variables["MacAddr"] = {
                    "value": observable_data.get("value"),
                }
            elif type == "Mutex":
                input_variables["Mutex"] = {
                    "name": observable_data.get("name"),
                }
            elif type == "Network-Traffic":
                input_variables["NetworkTraffic"] = {
                    "start": observable_data.get("start"),
                    "end": observable_data.get("end"),
                    "is_active": observable_data.get("is_active"),
                    "src_port": observable_data.get("src_port"),
                    "dst_port": observable_data.get("dst_port"),
                    "protocols": observable_data.get("protocols"),
                    "src_byte_count": observable_data.get("src_byte_count"),
                    "dst_byte_count": observable_data.get("dst_byte_count"),
                    "src_packets": observable_data.get("src_packets"),
                    "dst_packets": observable_data.get("dst_packets"),
                }
            elif type == "Process":
                input_variables["Process"] = {
                    "is_hidden": observable_data.get("is_hidden"),
                    "pid": observable_data.get("pid"),
                    "created_time": observable_data.get("created_time"),
                    "cwd": observable_data.get("cwd"),
                    "command_line": observable_data.get("command_line"),
                    "environment_variables": observable_data.get(
                        "environment_variables"
                    ),
                }
            elif type == "Software":
                input_variables["Software"] = {
                    "name": observable_data.get("name"),
                    "cpe": observable_data.get("cpe"),
                    "swid": observable_data.get("swid"),
                    "languages": observable_data.get("languages"),
                    "vendor": observable_data.get("vendor"),
                    "version": observable_data.get("version"),
                }
            elif type == "Url":
                input_variables["Url"] = {
                    "value": observable_data.get("value"),
                }
            elif type == "User-Account":
                input_variables["UserAccount"] = {
                    "user_id": observable_data.get("user_id"),
                    "credential": observable_data.get("credential"),
                    "account_login": observable_data.get("account_login"),
                    "account_type": observable_data.get("account_type"),
                    "display_name": observable_data.get("display_name"),
                    "is_service_account": observable_data.get("is_service_account"),
                    "is_privileged": observable_data.get("is_privileged"),
                    "can_escalate_privs": observable_data.get("can_escalate_privs"),
                    "is_disabled": observable_data.get("is_disabled"),
                    "account_created": observable_data.get("account_created"),
                    "account_expires": observable_data.get("account_expires"),
                    "credential_last_changed": observable_data[
                        "credential_last_changed"
                    ]
                    if "credential_last_changed" in observable_data
                    else None,
                    "account_first_login": observable_data.get("account_first_login"),
                    "account_last_login": observable_data.get("account_last_login"),
                }
            elif type == "Windows-Registry-Key":
                input_variables["WindowsRegistryKey"] = {
                    "attribute_key": observable_data.get("key"),
                    "modified_time": observable_data.get("modified_time"),
                    "number_of_subkeys": observable_data.get("number_of_subkeys"),
                }
            elif type == "Windows-Registry-Value-Type":
                input_variables["WindowsRegistryKeyValueType"] = {
                    "name": observable_data.get("name"),
                    "data": observable_data.get("data"),
                    "data_type": observable_data.get("data_type"),
                }
            elif type == "Cryptographic-Key":
                input_variables["CryptographicKey"] = {
                    "value": observable_data.get("value"),
                }
            elif (
                type == "Cryptocurrency-Wallet"
                or type == "X-OpenCTI-Cryptocurrency-Wallet"
            ):
                input_variables["CryptocurrencyWallet"] = {
                    "value": observable_data.get("value"),
                }
            elif type == "Hostname":
                input_variables["Hostname"] = {
                    "value": observable_data.get("value"),
                }
            elif type == "Text":
                input_variables["Text"] = {
                    "value": observable_data.get("value"),
                }
            elif type == "User-Agent":
                input_variables["UserAgent"] = {
                    "value": observable_data.get("value"),
                }
            result = self.opencti.query(query, input_variables)
            return self.opencti.process_multiple_fields(
                result["data"]["stixCyberObservableAdd"]
            )
        else:
            self.opencti.log("error", "Missing parameters: type")

    """
        Upload an artifact

        :param file_path: the file path
        :return Stix-Observable object
    """

    def upload_artifact(self, **kwargs):
        file_name = kwargs.get("file_name", None)
        data = kwargs.get("data", None)
        mime_type = kwargs.get("mime_type", "text/plain")
        x_opencti_description = kwargs.get("x_opencti_description", False)
        created_by = kwargs.get("createdBy", None)
        object_marking = kwargs.get("objectMarking", None)
        object_label = kwargs.get("objectLabel", None)
        create_indicator = kwargs.get("createIndicator", False)

        if file_name is not None and mime_type is not None:
            final_file_name = os.path.basename(file_name)
            self.opencti.log(
                "info",
                "Creating Stix-Cyber-Observable {artifact}} with indicator at "
                + str(create_indicator)
                + ".",
            )
            query = """
                mutation ArtifactImport($file: Upload!, $x_opencti_description: String, $createdBy: String, $objectMarking: [String], $objectLabel: [String]) {
                    artifactImport(file: $file, x_opencti_description: $x_opencti_description, createdBy: $createdBy, objectMarking: $objectMarking, objectLabel: $objectLabel) {
                        id
                        standard_id
                        entity_type
                        parent_types
                        spec_version
                        created_at
                        updated_at
                        createdBy {
                            ... on Identity {
                                id
                                standard_id
                                entity_type
                                parent_types
                                spec_version
                                name
                                description
                                roles
                                contact_information
                                x_opencti_aliases
                                created
                                modified
                                objectLabel {
                                    edges {
                                        node {
                                            id
                                            value
                                            color
                                        }
                                    }
                                }
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
                        observable_value
                        x_opencti_description
                        x_opencti_score
                        indicators {
                            edges {
                                node {
                                    id
                                    pattern
                                    pattern_type
                                }
                            }
                        }
                        mime_type
                        payload_bin
                        url
                        encryption_algorithm
                        decryption_key
                        hashes {
                            algorithm
                            hash
                        }
                        importFiles {
                            edges {
                                node {
                                    id
                                    name
                                    size
                                }
                            }
                        }
                    }
                }
            """
            if data is None:
                data = open(file_name, "rb")
                if file_name.endswith(".json"):
                    mime_type = "application/json"
                else:
                    mime_type = magic.from_file(file_name, mime=True)

            result = self.opencti.query(
                query,
                {
                    "file": (self._file_type(final_file_name, data, mime_type)),
                    "x_opencti_description": x_opencti_description,
                    "createdBy": created_by,
                    "objectMarking": object_marking,
                    "objectLabel": object_label,
                },
            )
            return self.opencti.process_multiple_fields(
                result["data"]["artifactImport"]
            )
        else:
            self.opencti.log("error", "Missing parameters: type")

    """
        Update a Stix-Observable object field

        :param id: the Stix-Observable id
        :param input: the input of the field
        :return The updated Stix-Observable object
    """

    def update_field(self, **kwargs):
        id = kwargs.get("id", None)
        input = kwargs.get("input", None)
        if id is not None and input is not None:
            self.opencti.log("info", "Updating Stix-Observable {" + id + "}.")
            query = """
                mutation StixCyberObservableEdit($id: ID!, $input: [EditInput]!) {
                    stixCyberObservableEdit(id: $id) {
                        fieldPatch(input: $input) {
                            id
                            standard_id
                            entity_type
                        }
                    }
                }
            """
            result = self.opencti.query(
                query,
                {
                    "id": id,
                    "input": input,
                },
            )
            return self.opencti.process_multiple_fields(
                result["data"]["stixCyberObservableEdit"]["fieldPatch"]
            )
        else:
            self.opencti.log(
                "error",
                "[opencti_stix_cyber_observable_update_field] Missing parameters: id and input",
            )
            return None

    """
        Promote a Stix-Observable to an Indicator

        :param id: the Stix-Observable id
        :return void
    """

    def promote_to_indicator(self, **kwargs):
        id = kwargs.get("id", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id is not None:
            self.opencti.log("info", "Promoting Stix-Observable {" + id + "}.")
            query = (
                """
                        mutation StixCyberObservableEdit($id: ID!) {
                            stixCyberObservableEdit(id: $id) {
                                promote {
                                    """
                + (
                    custom_attributes
                    if custom_attributes is not None
                    else self.properties
                )
                + """    
                            }                               
                        }
                    }
             """
            )
            result = self.opencti.query(query, {"id": id})
            return self.opencti.process_multiple_fields(
                result["data"]["stixCyberObservableEdit"]["promote"]
            )
        else:
            self.opencti.log(
                "error",
                "[opencti_stix_cyber_observable_promote] Missing parameters: id",
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
                     stixCyberObservableEdit(id: $id) {
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
        Update the Identity author of a Stix-Cyber-Observable object (created_by)

        :param id: the id of the Stix-Cyber-Observable
        :param identity_id: the id of the Identity
        :return Boolean
    """

    def update_created_by(self, **kwargs):
        id = kwargs.get("id", None)
        identity_id = kwargs.get("identity_id", None)
        if id is not None:
            self.opencti.log(
                "info",
                "Updating author of Stix-Cyber-Observable {"
                + id
                + "} with Identity {"
                + str(identity_id)
                + "}",
            )
            custom_attributes = """
                id
                createdBy {
                    ... on Identity {
                        id
                        standard_id
                        entity_type
                        parent_types
                        name
                        x_opencti_aliases
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
            """
            stix_domain_object = self.read(id=id, customAttributes=custom_attributes)
            if stix_domain_object["createdBy"] is not None:
                query = """
                    mutation StixCyberObservableEdit($id: ID!, $toId: String! $relationship_type: String!) {
                        stixCyberObservableEdit(id: $id) {
                            relationDelete(toId: $toId, relationship_type: $relationship_type) {
                                id
                            }
                        }
                    }
                """
                self.opencti.query(
                    query,
                    {
                        "id": id,
                        "toId": stix_domain_object["createdBy"]["id"],
                        "relationship_type": "created-by",
                    },
                )
            if identity_id is not None:
                # Add the new relation
                query = """
                    mutation StixCyberObservableEdit($id: ID!, $input: StixMetaRelationshipAddInput) {
                        stixCyberObservableEdit(id: $id) {
                            relationAdd(input: $input) {
                                id
                            }
                        }
                    }
               """
                variables = {
                    "id": id,
                    "input": {
                        "toId": identity_id,
                        "relationship_type": "created-by",
                    },
                }
                self.opencti.query(query, variables)
        else:
            self.opencti.log("error", "Missing parameters: id")
            return False

    """
        Add a Marking-Definition object to Stix-Cyber-Observable object (object_marking_refs)

        :param id: the id of the Stix-Cyber-Observable
        :param marking_definition_id: the id of the Marking-Definition
        :return Boolean
    """

    def add_marking_definition(self, **kwargs):
        id = kwargs.get("id", None)
        marking_definition_id = kwargs.get("marking_definition_id", None)
        if id is not None and marking_definition_id is not None:
            custom_attributes = """
                id
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
            """
            stix_cyber_observable = self.read(id=id, customAttributes=custom_attributes)
            if stix_cyber_observable is None:
                self.opencti.log(
                    "error", "Cannot add Marking-Definition, entity not found"
                )
                return False
            if marking_definition_id in stix_cyber_observable["objectMarkingIds"]:
                return True
            else:
                self.opencti.log(
                    "info",
                    "Adding Marking-Definition {"
                    + marking_definition_id
                    + "} to Stix-Cyber-Observable {"
                    + id
                    + "}",
                )
                query = """
                   mutation StixCyberObservableAddRelation($id: ID!, $input: StixMetaRelationshipAddInput) {
                       stixCyberObservableEdit(id: $id) {
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
                            "toId": marking_definition_id,
                            "relationship_type": "object-marking",
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
        Remove a Marking-Definition object to Stix-Cyber-Observable object

        :param id: the id of the Stix-Cyber-Observable
        :param marking_definition_id: the id of the Marking-Definition
        :return Boolean
    """

    def remove_marking_definition(self, **kwargs):
        id = kwargs.get("id", None)
        marking_definition_id = kwargs.get("marking_definition_id", None)
        if id is not None and marking_definition_id is not None:
            self.opencti.log(
                "info",
                "Removing Marking-Definition {"
                + marking_definition_id
                + "} from Stix-Cyber-Observable {"
                + id
                + "}",
            )
            query = """
               mutation StixCyberObservableRemoveRelation($id: ID!, $toId: String!, $relationship_type: String!) {
                   stixCyberObservableEdit(id: $id) {
                        relationDelete(toId: $toId, relationship_type: $relationship_type) {
                            id
                        }
                   }
               }
            """
            self.opencti.query(
                query,
                {
                    "id": id,
                    "toId": marking_definition_id,
                    "relationship_type": "object-marking",
                },
            )
            return True
        else:
            self.opencti.log("error", "Missing parameters: id and label_id")
            return False

    """
        Add a Label object to Stix-Cyber-Observable object

        :param id: the id of the Stix-Cyber-Observable
        :param label_id: the id of the Label
        :return Boolean
    """

    def add_label(self, **kwargs):
        id = kwargs.get("id", None)
        label_id = kwargs.get("label_id", None)
        label_name = kwargs.get("label_name", None)
        if label_name is not None:
            label = self.opencti.label.read(
                filters=[{"key": "value", "values": [label_name]}]
            )
            if label:
                label_id = label["id"]
            else:
                label = self.opencti.label.create(value=label_name)
                label_id = label["id"]
        if id is not None and label_id is not None:
            self.opencti.log(
                "info",
                "Adding label {" + label_id + "} to Stix-Cyber-Observable {" + id + "}",
            )
            query = """
               mutation StixCyberObservableAddRelation($id: ID!, $input: StixMetaRelationshipAddInput) {
                   stixCyberObservableEdit(id: $id) {
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
                        "toId": label_id,
                        "relationship_type": "object-label",
                    },
                },
            )
            return True
        else:
            self.opencti.log("error", "Missing parameters: id and label_id")
            return False

    """
        Remove a Label object to Stix-Cyber-Observable object

        :param id: the id of the Stix-Cyber-Observable
        :param label_id: the id of the Label
        :return Boolean
    """

    def remove_label(self, **kwargs):
        id = kwargs.get("id", None)
        label_id = kwargs.get("label_id", None)
        label_name = kwargs.get("label_name", None)
        if label_name is not None:
            label = self.opencti.label.read(
                filters=[{"key": "value", "values": [label_name]}]
            )
            if label:
                label_id = label["id"]
        if id is not None and label_id is not None:
            self.opencti.log(
                "info",
                "Removing label {"
                + label_id
                + "} to Stix-Cyber-Observable {"
                + id
                + "}",
            )
            query = """
               mutation StixCyberObservableRemoveRelation($id: ID!, $toId: String!, $relationship_type: String!) {
                   stixCyberObservableEdit(id: $id) {
                        relationDelete(toId: $toId, relationship_type: $relationship_type) {
                            id
                        }
                   }
               }
            """
            self.opencti.query(
                query,
                {
                    "id": id,
                    "toId": label_id,
                    "relationship_type": "object-label",
                },
            )
            return True
        else:
            self.opencti.log("error", "Missing parameters: id and label_id")
            return False

    """
        Add a External-Reference object to Stix-Cyber-Observable object (object_marking_refs)

        :param id: the id of the Stix-Cyber-Observable
        :param marking_definition_id: the id of the Marking-Definition
        :return Boolean
    """

    def add_external_reference(self, **kwargs):
        id = kwargs.get("id", None)
        external_reference_id = kwargs.get("external_reference_id", None)
        if id is not None and external_reference_id is not None:
            custom_attributes = """
                id
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
            """
            stix_domain_object = self.read(id=id, customAttributes=custom_attributes)
            if stix_domain_object is None:
                self.opencti.log(
                    "error", "Cannot add External-Reference, entity not found"
                )
                return False
            if external_reference_id in stix_domain_object["externalReferencesIds"]:
                return True
            else:
                self.opencti.log(
                    "info",
                    "Adding External-Reference {"
                    + external_reference_id
                    + "} to Stix-Cyber-Observable {"
                    + id
                    + "}",
                )
                query = """
                   mutation StixCyberObservabletEditRelationAdd($id: ID!, $input: StixMetaRelationshipAddInput) {
                       stixCyberObservableEdit(id: $id) {
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
        Remove a Label object to Stix-Cyber-Observable object

        :param id: the id of the Stix-Cyber-Observable
        :param label_id: the id of the Label
        :return Boolean
    """

    def remove_external_reference(self, **kwargs):
        id = kwargs.get("id", None)
        external_reference_id = kwargs.get("external_reference_id", None)
        if id is not None and external_reference_id is not None:
            self.opencti.log(
                "info",
                "Removing External-Reference {"
                + external_reference_id
                + "} to Stix-Cyber-Observable {"
                + id
                + "}",
            )
            query = """
               mutation StixCyberObservableRemoveRelation($id: ID!, $toId: String!, $relationship_type: String!) {
                   stixCyberObservableEdit(id: $id) {
                        relationDelete(toId: $toId, relationship_type: $relationship_type) {
                            id
                        }
                   }
               }
            """
            self.opencti.query(
                query,
                {
                    "id": id,
                    "toId": external_reference_id,
                    "relationship_type": "external-reference",
                },
            )
            return True
        else:
            self.opencti.log("error", "Missing parameters: id and label_id")
            return False

    def push_list_export(self, file_name, data, list_filters=""):
        query = """
            mutation StixCyberObservablesExportPush($file: Upload!, $listFilters: String) {
                stixCyberObservablesExportPush(file: $file, listFilters: $listFilters)
            }
        """
        self.opencti.query(
            query,
            {
                "file": (self._file_type(file_name, data)),
                "listFilters": list_filters,
            },
        )

    def ask_for_enrichment(self, **kwargs) -> str:
        id = kwargs.get("id", None)
        connector_id = kwargs.get("connector_id", None)

        if id is None or connector_id is None:
            self.opencti.log("error", "Missing parameters: id and connector_id")
            return ""

        query = """
            mutation StixCoreObjectEnrichmentLinesMutation($id: ID!, $connectorId: ID!) {
                stixCoreObjectEdit(id: $id) {
                    askEnrichment(connectorId: $connectorId) {
                        id
                    }
                }
            }
            """

        result = self.opencti.query(
            query,
            {
                "id": id,
                "connectorId": connector_id,
            },
        )
        # return work_id
        return result["data"]["stixCoreObjectEdit"]["askEnrichment"]["id"]

    """
        Get the reports about a Stix-Cyber-Observable object

        :param id: the id of the Stix-Cyber-Observable
        :return List of reports
    """

    def reports(self, **kwargs):
        id = kwargs.get("id", None)
        if id is not None:
            self.opencti.log(
                "info",
                "Getting reports of the Stix-Cyber-Observable {" + id + "}.",
            )
            query = """
                query StixCyberObservable($id: String!) {
                    stixCyberObservable(id: $id) {
                        reports {
                            edges {
                                node {
                                    id
                                    standard_id
                                    entity_type
                                    parent_types
                                    spec_version
                                    created_at
                                    updated_at
                                    createdBy {
                                        ... on Identity {
                                            id
                                            standard_id
                                            entity_type
                                            parent_types
                                            spec_version
                                            identity_class
                                            name
                                            description
                                            roles
                                            contact_information
                                            x_opencti_aliases
                                            created
                                            modified
                                            objectLabel {
                                                edges {
                                                    node {
                                                        id
                                                        value
                                                        color
                                                    }
                                                }
                                            }
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
                                                importFiles {
                                                    edges {
                                                        node {
                                                            id
                                                            name
                                                            size
                                                            metaData {
                                                                mimetype
                                                                version
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                    revoked
                                    confidence
                                    created
                                    modified
                                    name
                                    description
                                    report_types
                                    published                                    
                                }
                            }
                        }
                    }
                }
             """
            result = self.opencti.query(query, {"id": id})
            processed_result = self.opencti.process_multiple_fields(
                result["data"]["stixCyberObservable"]
            )
            if processed_result:
                return processed_result["reports"]
            else:
                return []
        else:
            self.opencti.log("error", "Missing parameters: id")
            return None

    """
        Get the notes about a Stix-Cyber-Observable object

        :param id: the id of the Stix-Cyber-Observable
        :return List of notes
    """

    def notes(self, **kwargs):
        id = kwargs.get("id", None)
        if id is not None:
            self.opencti.log(
                "info",
                "Getting notes of the Stix-Cyber-Observable {" + id + "}.",
            )
            query = """
                query StixCyberObservable($id: String!) {
                    stixCyberObservable(id: $id) {
                        notes {
                            edges {
                                node {
                                    id
                                    standard_id
                                    entity_type
                                    parent_types
                                    spec_version
                                    created_at
                                    updated_at
                                    createdBy {
                                        ... on Identity {
                                            id
                                            standard_id
                                            entity_type
                                            parent_types
                                            spec_version
                                            identity_class
                                            name
                                            description
                                            roles
                                            contact_information
                                            x_opencti_aliases
                                            created
                                            modified
                                            objectLabel {
                                                edges {
                                                    node {
                                                        id
                                                        value
                                                        color
                                                    }
                                                }
                                            }
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
                                                importFiles {
                                                    edges {
                                                        node {
                                                            id
                                                            name
                                                            size
                                                            metaData {
                                                                mimetype
                                                                version
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                    revoked
                                    confidence
                                    created
                                    modified
                                    attribute_abstract
                                    content
                                    authors                                
                                }
                            }
                        }
                    }
                }
             """
            result = self.opencti.query(query, {"id": id})
            processed_result = self.opencti.process_multiple_fields(
                result["data"]["stixCyberObservable"]
            )
            if processed_result:
                return processed_result["notes"]
            else:
                return []
        else:
            self.opencti.log("error", "Missing parameters: id")
            return None

    """
        Get the observed data of a Stix-Cyber-Observable object

        :param id: the id of the Stix-Cyber-Observable
        :return List of observed data
    """

    def observed_data(self, **kwargs):
        id = kwargs.get("id", None)
        if id is not None:
            self.opencti.log(
                "info",
                "Getting Observed-Data of the Stix-Cyber-Observable {" + id + "}.",
            )
            query = """
                    query StixCyberObservable($id: String!) {
                        stixCyberObservable(id: $id) {
                            observedData {
                                edges {
                                    node {
                                        id
                                        standard_id
                                        entity_type
                                        parent_types
                                        spec_version
                                        created_at
                                        updated_at
                                        createdBy {
                                            ... on Identity {
                                                id
                                                standard_id
                                                entity_type
                                                parent_types
                                                spec_version
                                                identity_class
                                                name
                                                description
                                                roles
                                                contact_information
                                                x_opencti_aliases
                                                created
                                                modified
                                                objectLabel {
                                                    edges {
                                                        node {
                                                            id
                                                            value
                                                            color
                                                        }
                                                    }
                                                }
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
                                                    importFiles {
                                                        edges {
                                                            node {
                                                                id
                                                                name
                                                                size
                                                                metaData {
                                                                    mimetype
                                                                    version
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                        revoked
                                        confidence
                                        created
                                        modified
                                        first_observed
                                        last_observed
                                        number_observed
                                        importFiles {
                                            edges {
                                                node {
                                                    id
                                                    name
                                                    size
                                                    metaData {
                                                        mimetype
                                                        version
                                                    }
                                                }
                                            }
                                        }    
                                    }
                                }
                            }
                        }
                    }
                 """
            result = self.opencti.query(query, {"id": id})
            processed_result = self.opencti.process_multiple_fields(
                result["data"]["stixCyberObservable"]
            )
            if processed_result:
                return processed_result["observedData"]
            else:
                return []
        else:
            self.opencti.log("error", "Missing parameters: id")
            return None
